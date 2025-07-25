import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import math

# Page headers
st.set_page_config(page_title="Trading Strategy Performance Visualizer", layout="wide", page_icon="📈")

st.title("💸 Trading Strategy Performance Visualizer")
st.markdown("""
**Simulate 100 Possible Futures for Your Trading Strategy**  
*This calculator models probabilistic outcomes based on your win rate, risk/reward, and position sizing*
""")


def calculate_expectancy(win_probability, win_reward):
    return round(win_probability / 100 * win_reward - (1-win_probability/100), 2)


def calculate_kelly_criterion(win_probability, win_reward):
    win_decimal = win_probability / 100
    loss_decimal = 1 - win_decimal
    return round((win_decimal-(loss_decimal/win_reward)), 4)


@st.cache_data(show_spinner="Running 100 simulations... This takes ~10-30 seconds",
               ttl=3600,  # Keep for 1 hour
               hash_funcs={pd.DataFrame: lambda _: None})  # Don't hash large DataFrames
def calculate_simulated_results(win_probability, win_reward_r, no_of_opportunities, no_periods,
                                no_cycles, starting_balance, ending_balance,
                                add_value, add_period,
                                withdraw_value, withdraw_period,
                                taxes_value, taxes_period, user_risk, user_risk_period):
    """
    Runs Monte Carlo simulation of trading strategy performance

    Parameters:
    win_probability (int): Win rate percentage (1-100)
    win_reward_r (float): Reward:Risk ratio
    no_of_opportunities (int): Trades per period
    no_periods (int): Periods per cycle
    no_cycles (int): Total cycles to simulate
    starting_balance (float): Initial account balance
    ending_balance (float): Target account balance
    add_value (float): Regular contributions amount
    add_period (str): 'Period' or 'Cycle' for contributions
    withdraw_value (float): Regular withdrawals amount
    withdraw_period (str): 'Period' or 'Cycle' for withdrawals
    taxes_value (float): Tax rate percentage (0-100)
    taxes_period (str): 'Period' or 'Cycle' for tax payments
    user_risk (float): Risk percentage per trade
    user_risk_period (str): When to adjust risk % ('Period'/'Cycle')

    Returns:
    DataFrame: Simulation results with columns:
        [Sim, Cycle, Period, Wins, Losses, Win Rate,
         Start Balance, Risk, Return, Added, Withdrawn,
         Tax, End Balance, Peak Balance, Drawdown, Drawdown pct]
    """
    # Create DataFrame for the compound rate results
    result_df = pd.DataFrame()

    # Enter the loop - cycles contains periods
    list_of_possible_r_outcomes = [win_reward_r, -1]
    for simulation in range(1, 101):
        start_balance = starting_balance
        # Set the initial risk before entering the new cycle loop
        risk_per_trade = round(start_balance * user_risk / 100, 0)

        for cycle in range(1, no_cycles + 1):
            return_per_cycle = []
            # Generate list of trade outcomes per cycle
            list_of_trade_outcomes = random.choices(
                list_of_possible_r_outcomes,
                weights=[win_probability, 100 - win_probability],
                k=no_of_opportunities * no_periods
            )

            for period in range(1, no_periods + 1):
                # Work only until the account target has been reached
                if (start_balance >= ending_balance) or (start_balance <= 0):
                    break
                # Adjust risk if user adapts risk per cycle or per period
                # in other cases or never it nothing is chosen
                if (period == 1) and (user_risk_period == "Cycle"):
                    risk_per_trade = round(start_balance * user_risk / 100, 0)
                elif user_risk_period == "Period":
                    risk_per_trade = round(start_balance * user_risk / 100, 0)
                else:
                    risk_per_trade = risk_per_trade

                # Calculations required per period
                list_of_trade_outcomes_in_period = list_of_trade_outcomes[
                                                   period * no_of_opportunities - no_of_opportunities:period * no_of_opportunities]
                real_r_return_per_period = sum(list_of_trade_outcomes_in_period)

                no_of_wins_in_period = list_of_trade_outcomes_in_period.count(list_of_possible_r_outcomes[0])
                no_of_loses_in_period = len(list_of_trade_outcomes_in_period) - no_of_wins_in_period
                return_on_period = real_r_return_per_period * risk_per_trade
                return_per_cycle.append(return_on_period)
                tax_withheld = round(return_on_period * taxes_value / 100, 0) if taxes_period == "Period" else 0
                add_to_account = add_value if add_period == "Period" else 0
                withdraw_from_account = withdraw_value if withdraw_period == "Period" else 0

                # Calculations required if user choose Cycle in some cases rather than Period
                if period == no_periods:
                    add_to_account = add_value if add_period == "Cycle" else add_to_account
                    withdraw_from_account = withdraw_value if withdraw_period == "Cycle" else withdraw_from_account
                    tax_withheld = sum(
                        return_per_cycle) * taxes_value / 100 if taxes_period == "Cycle" else tax_withheld

                end_balance = round(
                    start_balance + return_on_period + add_to_account - withdraw_from_account - tax_withheld, 0)

                # Create new row per each period and later concatenate it with the existing DataFrame
                new_row_df = pd.DataFrame(
                    {
                        "Sim": simulation,
                        "Cycle": cycle,
                        "Period": period,
                        "Wins": no_of_wins_in_period,
                        "Losses": no_of_loses_in_period,
                        "Win Rate": no_of_wins_in_period / len(list_of_trade_outcomes_in_period) * 100,
                        "Start Balance": start_balance,
                        "Risk": risk_per_trade,
                        "Return": return_on_period,
                        "Added": add_to_account,
                        "Withdrawn": withdraw_from_account,
                        "Tax": tax_withheld,
                        "End Balance": end_balance
                    },
                    index=[0])

                result_df = pd.concat([result_df, new_row_df], ignore_index=True)
                result_df['Peak Balance'] = result_df.groupby('Sim')[
                    'End Balance'].cummax()
                result_df['Drawdown'] = result_df['Peak Balance'] - result_df['End Balance']
                result_df['Drawdown pct'] = round(
                    (result_df['Peak Balance'] - result_df['End Balance']) / result_df['Peak Balance'] * 100, 1)

                start_balance = end_balance

    return result_df


def create_user_form():
    with st.form(key="Setup calculations"):
        # Trading System Setup Section
        col1, col2 = st.columns(2)
        with col1:
            st.header("🧮 Strategy Setup")
            st.subheader("Trading System")
            win_probability_pct = st.slider(
                "**Win Probability (%)**",
                min_value=1,
                max_value=100,
                value=40,
                help="Percentage of trades that are winners"
            )

            win_reward_R = st.slider(
                "**Reward to Risk Ratio**",
                min_value=0.1,
                max_value=20.0,
                value=2.0,
                step=0.1,
                help="Profit potential relative to your risk (e.g., 2.0 = 2:1 ratio)"
            )

            st.subheader("Time Horizon")
            no_of_opportunities_per_period = st.slider(
                "**Opportunities per Period**",
                min_value=1,
                max_value=100,
                value=10,
                help="Number of trading opportunities in a given time period"
            )

            no_of_periods = st.slider(
                "**Periods per Cycle**",
                min_value=1,
                max_value=200,
                value=12,
                help="Number of periods in each cycle (e.g., months in a year)"
            )

            no_of_cycles = st.slider(
                "**Number of Cycles**",
                min_value=1,
                max_value=50,
                value=30,
                help="Total cycles to simulate (e.g., years)"
            )

        with col2:
            st.header("💰Account Management")
            # Use list as an input for Period or Cycle choice
            period_cycle_choice = ["Period", "Cycle"]

            # Container for account balance - we want to know starting balance and the users target
            with st.container():
                st.subheader("Capital Setup")
                col_balance_1, col_balance_2 = st.columns(2)
                with col_balance_1:
                    starting_account_balance = st.number_input(
                        "Start Account Balance",
                        min_value=500,
                        max_value=1000000,
                        value=1000,
                        help="Initial trading capital"
                    )
                with col_balance_2:
                    ending_account_balance = st.number_input(
                        "End Account Balance",
                        min_value=starting_account_balance,
                        max_value=100000000,
                        value=1000000,
                        help="Financial target"
                    )

            # We want to know if user wants to add to the account per period or cycle
            with st.container():
                st.subheader("Cash Flows")
                col_add_1, col_add_2 = st.columns(2)
                with col_add_1:
                    add_to_account_value = st.number_input(
                        "Regular Contributions($)",
                        min_value=0,
                        max_value=10000,
                        value=0,
                        help="Amount added to account regularly"
                    )
                with col_add_2:
                    add_to_account_period = st.segmented_control(
                        "Contribution Frequency",
                        period_cycle_choice,
                        key="Add period",
                        help="When contributions are made"
                    )

            # We want to know if user wants to add to the account per period or cycle
            with st.container():
                col_withdraw_1, col_withdraw_2 = st.columns(2)
                with col_withdraw_1:
                    withdraw_from_account_value = st.number_input(
                        "Regular Withdrawals ($)",
                        min_value=0,
                        max_value=10000,
                        value=0,
                        help="Amount withdrawn from account regularly"
                    )
                with col_withdraw_2:
                    withdraw_from_account_period = st.segmented_control(
                        "Withdrawal Frequency",
                        period_cycle_choice,
                        key="Withdraw period",
                        help="User wants to withdraw certain amount of money to the account per Period or Cycle"
                    )

            # Tax
            with st.container():
                st.subheader("Risk & Tax Management")
                col_tax_1, col_tax_2 = st.columns(2)
                with col_tax_1:
                    tax_value_pct = st.slider(
                        "Capital Gains Tax",
                        min_value=0,
                        max_value=100,
                        value=0,
                        step=1,
                        help="Tax rate on profits"
                    )
                with col_tax_2:
                    tax_period = st.segmented_control(
                        "Pay Tax every:",
                        period_cycle_choice,
                        key="Tax period",
                        help="When taxes are paid"
                    )

            # Risk Management
            with st.container():
                col_risk_1, col_risk_2 = st.columns(2)
                with col_risk_1:
                    user_risk_pct = st.number_input(
                        "Risk per trade as a % of bankroll",
                        min_value=0.1,
                        max_value=100.00,
                        value=2.0,
                        step=0.1,
                        help="Percentage of capital risked per trade"
                    )
                with col_risk_2:
                    user_risk_adj_period = st.segmented_control(
                        "Adjust Risk every:",
                        period_cycle_choice,
                        key="Adjust risk period",
                        help="When risk percentage is recalculated"
                    )
        st.form_submit_button("Calculate", on_click=clear_session_state)
    # End of FORM
    return {'win_probability_pct': win_probability_pct,
            'win_reward_R': win_reward_R,
            'no_of_opportunities_per_period': no_of_opportunities_per_period,
            'no_of_periods': no_of_periods,
            'no_of_cycles': no_of_cycles,
            'starting_account_balance': starting_account_balance,
            'ending_account_balance': ending_account_balance,
            'add_to_account_value': add_to_account_value,
            'add_to_account_period': add_to_account_period,
            'withdraw_from_account_value': withdraw_from_account_value,
            'withdraw_from_account_period': withdraw_from_account_period,
            'tax_value_pct': tax_value_pct,
            'tax_period': tax_period,
            'user_risk_pct': user_risk_pct,
            'user_risk_adj_period': user_risk_adj_period
            }


def clear_session_state():
    st.session_state.sim_to_show = 1
    return st.session_state.sim_to_show


def calculate_min_max_avg_cycle(df, no_of_periods):
    df = df.copy()
    df["In_Periods"] = df["END_Cycle"] * no_of_periods + df["END_Period"]
    min_periods = df["In_Periods"].min()
    max_periods = df["In_Periods"].max()
    avg_periods = df["In_Periods"].mean()
    return {
        "MIN_Cycle": math.floor(min_periods/no_of_periods),
        "MIN_Period": min_periods % no_of_periods,
        "MAX_Cycle": math.floor(max_periods/no_of_periods),
        "MAX_Period": max_periods % no_of_periods,
        "AVG_Cycle": math.floor(avg_periods/no_of_periods),
        "AVG_Period": avg_periods % no_of_periods
    }


def create_distribution_chart(df, df_label, x_label, y_label):
    fig_distribution = go.Figure(data=[go.Histogram(
        x=df,
        histnorm='probability',
        hovertemplate="%{y:,.2f}<extra></extra>",

    )])

    fig_distribution.update_layout(
        title=df_label,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode="x unified",
        template="plotly_white",
    )

    return fig_distribution


# Sidebar
with st.sidebar:
    st.header("📊 About Trading Performance")
    st.markdown("""
    **Monte Carlo Simulation Insights:**
    - Simulates 100 possible futures for your strategy
    - Accounts for random win/loss sequences
    - Models compounding with risk-adjusted position sizing
    - Model returns results per period, not per trade

    **Key Metrics Tracked:**
    - Account growth trajectory
    - Maximum drawdown
    - Risk of ruin
    - Time to reach target
    """)

    st.subheader("Performance Formula")
    st.markdown("""
    ```
    Ending Balance = Start Balance × (1 + Growth Rate)^n
    Growth Rate = Expectancy × Risk % × Opportunities
    ```
    """)

#
#     st.markdown("---")
#     st.markdown("### 📚 Educational Resources")
#     st.markdown("""
#     - [Risk Management Guide](https://clocktrades.com/risk-management)
#     - [Position Sizing Strategies](https://clocktrades.com/position-sizing)
#     - [Compounding Calculator](https://clocktrades.com/compounding)
#     """)

    st.markdown("---")
    st.markdown("Made by [ClockTrades](https://clocktrades.com)")
    st.caption("*Simulated results don't guarantee future performance*")

# Put everything in a FORM and return as a dictionary
user_inputs = create_user_form()

# Calculations section:
expectancy = calculate_expectancy(user_inputs['win_probability_pct'], user_inputs['win_reward_R'])
r_return_per_period = round(expectancy * user_inputs['no_of_opportunities_per_period'], 1)
kelly_percentage = calculate_kelly_criterion(user_inputs['win_probability_pct'], user_inputs['win_reward_R']) * 100
kelly_percentage = max(0, kelly_percentage)

# Strategy Summary
strategy_container = st.container()

with ((strategy_container)):
    st.header("📊 Strategy Performance Assumptions")
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    with col_metric1:
        st.metric("Expectancy/Trade", f"{expectancy}R", "Avg $ per $ risked",
                  help="(Win% × Avg Win) - (Loss% × Avg Loss)")
    with col_metric2:
        st.metric("Period Return", f"{r_return_per_period}R",
                            f"{user_inputs["no_of_opportunities_per_period"]} trades/period",
                            help="Expectancy × Opportunities per Period")
    with col_metric3:
        risk_status = "🟢 Conservative" if user_inputs['user_risk_pct'] < kelly_percentage / 2 else "🟠 Moderate" if user_inputs['user_risk_pct'] < kelly_percentage else "🔴 Aggressive"
        st.metric("Risk Level", f"{user_inputs['user_risk_pct']}%", risk_status, help=f"Kelly: {kelly_percentage:.1f}% | Half-Kelly: {kelly_percentage/2:.1f}%")
    with col_metric4:
        st.metric("Simulations", "100 runs", "Monte Carlo model", help="100 randomized sequences of wins/losses")


# Visualisation section
visualisation_container = st.container()
with (visualisation_container):
    st.header("🚀 Compounding Growth Simulation")
    st.markdown("""
    **Explore Different Simulation Outcomes**  
    *Each simulation shows how random win/loss sequences affect your results*
    """)

    # Calculate results
    compound_interest_result_df = calculate_simulated_results(
        user_inputs['win_probability_pct'], user_inputs['win_reward_R'],
        user_inputs['no_of_opportunities_per_period'], user_inputs['no_of_periods'],
        user_inputs['no_of_cycles'], user_inputs['starting_account_balance'],
        user_inputs['ending_account_balance'],
        user_inputs['add_to_account_value'], user_inputs['add_to_account_period'],
        user_inputs['withdraw_from_account_value'], user_inputs['withdraw_from_account_period'],
        user_inputs['tax_value_pct'], user_inputs['tax_period'],
        user_inputs['user_risk_pct'], user_inputs['user_risk_adj_period'])

    # Present data in tabs - one for table and one for chart
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary Metrics", "Summary Table", "Distributions", "Data Tables", "Charts"])
    with tab4:
        # Show DataFrame
        # sim_to_show = st.number_input("Simulation number to show", 1, 100, 1, key="sim_no_choice")

        if "sim_to_show" not in st.session_state:
            st.session_state.sim_to_show = 1

        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("◀ Previous Simulation", use_container_width=True):
                st.session_state.sim_to_show = max(1, st.session_state.sim_to_show - 1)
        with nav_col2:
            sim_num = st.number_input("Select Simulation", 1, 100, st.session_state.sim_to_show,
                                      key="sim_select", label_visibility="collapsed")
            st.session_state.sim_to_show = sim_num
        with nav_col3:
            if st.button("Next Simulation ▶", use_container_width=True):
                st.session_state.sim_to_show = min(100, st.session_state.sim_to_show + 1)

        st.progress(st.session_state.sim_to_show / 100,
                    f"Simulation {st.session_state.sim_to_show}/100")


        run_to_show_df = compound_interest_result_df[compound_interest_result_df["Sim"] == st.session_state.sim_to_show]

        st.dataframe(
            run_to_show_df.style.format(
                {
                    "Start Balance": "${:,.0f}",
                    "Wins": "{:,.0f}",
                    "Losses": "{:,.0f}",
                    "Win Rate": "{:,.1f}%",
                    "Risk": "${:,.0f}",
                    "Return": "${:,.0f}",
                    "Added": "${:,.0f}",
                    "Withdrawn": "${:,.0f}",
                    "Tax": "${:,.0f}",
                    "End Balance": "${:,.0f}",
                    "Peak Balance": "${:,.0f}",
                    "Drawdown": "(${:,.0f})",
                    "Drawdown pct": "{:,.1f}%",
                }
            ),
            hide_index=True, use_container_width=True)

    with tab5:
        # Present data in the container with tabs - one for chart, one for data table
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=run_to_show_df.index,
            y=run_to_show_df["End Balance"],
            mode="lines",
            line=dict(color='#3498db', width=3),
            hovertemplate="Cycle: %{customdata[0]}<br>Period: %{customdata[1]}<br>Balance: $%{y:,.0f}<extra></extra>",
            customdata=compound_interest_result_df[["Cycle", "Period"]],
        ))

        # # Target line
        # fig.add_hline(
        #     y=ending_account_balance,
        #     line_dash="dash",
        #     line_color="green",
        #     annotation_text=f"Target: ${ending_account_balance:,.0f}",
        #     annotation_position="bottom right"
        # )

        # Update layout
        fig.update_layout(
            title=f"Account Growth Over Time for Simulation no {st.session_state.sim_to_show}",
            xaxis_title="Period Sequence",
            yaxis_title="Account Balance ($)",
            hovermode="x unified",
            template="plotly_white",
        )
        st.plotly_chart(fig, config={"displayModeBar": False}, use_container_width=True)
        # else:
        #     st.warning("This expectancy value is not mathematically possible with positive risk:reward ratios")

    with tab2:
        summary_df = compound_interest_result_df.groupby("Sim").agg(
            END_Cycle=("Cycle", "last"),
            END_Period=("Period", "last"),
            END_Balance=("End Balance", "last"),
            AVG_Return=("Return", "mean"),
            AVG_WinRate=("Win Rate", "mean"),
            MAX_Drawdown=("Drawdown", "max"),
            MAX_Drawdown_pct=("Drawdown pct", "max")
        )
        st.dataframe(
            summary_df.style.format(
                {
                    "END_Cycle": "{:,.0f}",
                    "END_Period": "{:,.0f}",
                    "END_Balance": "${:,.0f}",
                    "AVG_Return": "${:,.0f}",
                    "AVG_WinRate": "{:,.1f}%",
                    "MAX_Drawdown": "${:,.0f}",
                    "MAX_Drawdown_pct": "{:,.1f}%",
                }
            ))

    # Summary statistics
    # TODO: Add max, min winning streak
    with tab1:
        no_ruin_summary_df = summary_df[summary_df["END_Balance"] > 0]
        min_end_balance = no_ruin_summary_df["END_Balance"].min()
        max_end_balance = no_ruin_summary_df["END_Balance"].max()
        avg_end_balance = no_ruin_summary_df["END_Balance"].mean()
        risk_of_ruin_pct = len(summary_df[summary_df["END_Balance"] <= 0])
        min_return_period = no_ruin_summary_df["AVG_Return"].min()
        max_return_period = no_ruin_summary_df["AVG_Return"].max()
        avg_return_period = no_ruin_summary_df["AVG_Return"].mean()
        max_drawdown = no_ruin_summary_df["MAX_Drawdown"].max()
        min_drawdown = no_ruin_summary_df["MAX_Drawdown"].min()
        avg_drawdown = no_ruin_summary_df["MAX_Drawdown"].mean()
        max_drawdown_pct = no_ruin_summary_df["MAX_Drawdown_pct"].max()
        min_drawdown_pct = no_ruin_summary_df["MAX_Drawdown_pct"].min()
        avg_drawdown_pct = no_ruin_summary_df["MAX_Drawdown_pct"].mean()
        min_max_avg_cycle = calculate_min_max_avg_cycle(no_ruin_summary_df[["END_Cycle", "END_Period"]],
                                                        user_inputs["no_of_periods"])

        with st.container():
            st.metric("Risk of Ruin", f"{risk_of_ruin_pct:,.1f}%", help="Chances of account blowout")

            row1a, row1b, row1c = st.columns(3)
            with row1a:
                st.metric("Minimum End Balance", f"${min_end_balance:,.0f}", help="The lowest of the ending balances")
            with row1b:
                st.metric("Maximum End Balance", f"${max_end_balance:,.0f}", help="The highest of the ending balances")
            with row1c:
                st.metric("Average End Balance", f"${avg_end_balance:,.0f}", help="The average of the ending balances")
            row2a, row2b, row2c = st.columns(3)
            with row2a:
                st.metric("Min Return Per Period", f"${min_return_period:,.1f}", help="Minimum expected return per Period")
            with row2b:
                st.metric("Max Return Per Period", f"${max_return_period:,.1f}", help="Maximum expected return per Period")
            with row2c:
                st.metric("Average Return Per Period", f"${avg_return_period:,.1f}", help="Average expected return per Period")
            row3a, row3b, row3c = st.columns(3)
            with row3a:
                st.metric("Minimum Drawdown", f"${min_drawdown:,.0f}", help="The lowest of the drawdowns")
            with row3b:
                st.metric("Maximum Drawdown", f"${max_drawdown:,.0f}", help="The highest of the drawdowns")
            with row3c:
                st.metric("Average Drawdown", f"${avg_drawdown:,.0f}", help="The average of the drawdowns")
            row4a, row4b, row4c = st.columns(3)
            with row4a:
                st.metric("Minimum Drawdown %", f"{min_drawdown_pct:,.1f}%", help="The lowest of the drawdowns in pct")
            with row4b:
                st.metric("Maximum Drawdown %", f"{max_drawdown_pct:,.1f}%", help="The highest of the drawdowns in pct")
            with row4c:
                st.metric("Average Drawdown %", f"{avg_drawdown_pct:,.1f}%", help="The average of the drawdowns in pct")
            row5a, row5b, row5c = st.columns(3)
            with row5a:
                st.metric("Minimum Cycle/Period",
                          f"{min_max_avg_cycle['MIN_Cycle']:,.0f}/{min_max_avg_cycle['MIN_Period']:,.0f}", help="The lowest cycle/period")
            with row5b:
                st.metric("Maximum Cycle/Period",
                          f"{min_max_avg_cycle['MAX_Cycle']:,.0f}/{min_max_avg_cycle['MAX_Period']:,.0f}",
                          help="The highest cycle/period")
            with row5c:
                st.metric("Average Cycle/Period",
                          f"{min_max_avg_cycle['AVG_Cycle']:,.0f}/{min_max_avg_cycle['AVG_Period']:,.0f}",
                          help="The average cycle/period")
    with tab3:
        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.plotly_chart(
                create_distribution_chart(
                    no_ruin_summary_df["AVG_Return"],
                    "Distribution of Average Returns per Period",
                    "Average Returns $",
                    "Probability"
                ),
                config={"displayModeBar": False},
                use_container_width=True)
        with col_ch2:
            st.plotly_chart(
                create_distribution_chart(
                    no_ruin_summary_df["END_Balance"],
                    "Distribution of End Balances",
                    "End Balance $",
                    "Probability"),
                config={"displayModeBar": False},
                use_container_width=True)
        col_ch3, col_ch4 = st.columns(2)
        with col_ch3:
            st.plotly_chart(
                create_distribution_chart(
                    no_ruin_summary_df["MAX_Drawdown"],
                    "Distribution of Maximum Drawdowns",
                    "Maximum Drawdowns $",
                    "Probability"),
                config={"displayModeBar": False},
                use_container_width=True)
        with col_ch4:
            st.plotly_chart(
                create_distribution_chart(
                    no_ruin_summary_df["MAX_Drawdown_pct"],
                    "Distribution of Maximum Drawdowns in Percentage Points",
                    "Maximum Drawdowns %",
                    "Probability"),
                config={"displayModeBar": False},
                use_container_width=True)

# Explanation
with st.expander("💡 How to Interpret These Results", expanded=True):
    st.markdown(f"""
    ### Understanding Your Simulation Results

    **Strategy Profile:**
    - **{user_inputs['win_probability_pct']}% win rate** with **{user_inputs['win_reward_R']}:1 risk-reward ratio**
    - Risking **{user_inputs['user_risk_pct']}%** of account per trade
    - **Kelly-optimal risk: {kelly_percentage:.1f}%** | **Half-Kelly: {kelly_percentage / 2:.1f}%**

    **Key Observations from 100 Simulations:**
    1. **Success Rate**: {100 - risk_of_ruin_pct}% of simulations reached the target without ruin
    2. **Growth Pattern**: {'Exponential' if expectancy > 0.3 else 'Linear' if expectancy > 0 else 'Negative'} growth profile
    3. **Volatility**: Typical drawdowns between {min_drawdown_pct:.1f}%-{max_drawdown_pct:.1f}%
    """)

# Footer
st.markdown("---")
st.caption("© 2025 ClockTrades.com • All calculations are theoretical and don't guarantee future results • "
           "Risk management is essential in trading")
