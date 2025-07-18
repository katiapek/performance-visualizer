import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# Page headers
st.set_page_config(page_title="Trading Strategy Performance Visualizer", layout="wide", page_icon="📈")

st.title("💸 Trading Strategy Performance Visualizer")
st.markdown("""
**Visualize how ...**  
*This calculator visualizes...*
""")


def calculate_expectancy(win_probability, win_reward):
    return round(win_probability / 100 * win_reward - (1-win_probability/100), 2)


def calculate_kelly_criterion(win_probability, win_reward):
    win_decimal = win_probability / 100
    loss_decimal = 1 - win_decimal
    return round((win_decimal-(loss_decimal/win_reward)), 4)


# Sidebar
with st.sidebar:
    st.header("About Performance")
    st.markdown("""
    **Formula**: `Earn and not ruin (lol)`
    - **A**: End balance
    - **P**: Starting balance
    - **r**: Expected return per period (based on expectancy)
    - **n**: Number of compounding periods per cycle
    - **t**: Number of cycles

    In trading, we compound the **risk per trade** (adjusted as a percentage of the account balance), factoring in wins, losses, taxes, and cash flows.
    """)
    st.markdown("---")
    st.markdown("For more Free Tools Visit:")
    st.markdown("[ClockTrades.com - Free Trading Tools](https://clocktrades.com/free-trading-tools/)")
    st.caption("*For educational purposes only*")

# Put everything in a FORM
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
    st.form_submit_button("Calculate")
# End of FORM

# Calculations section:
expectancy = calculate_expectancy(win_probability_pct, win_reward_R)
r_return_per_period = round(expectancy * no_of_opportunities_per_period, 1)
kelly_percentage = calculate_kelly_criterion(win_probability_pct, win_reward_R) * 100
kelly_percentage = max(0, kelly_percentage)

# Strategy Summary
strategy_container = st.container()

with strategy_container:
    st.header("📊 Strategy Performance Assumptions")
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    with col_metric1:
        st.metric("Expectancy per Trade", f"{expectancy}R", help="Average return per $1 risked")
    with col_metric2:
        st.metric("Period Return", f"{r_return_per_period}R", help="Total return per period")
    with col_metric3:
        st.metric("Kelly Criterion", f"{kelly_percentage:.2f}%", help="Optimal risk percentage")
    with col_metric4:
        risk_comparison = "✅ Below Kelly" if user_risk_pct < kelly_percentage else "⚠️ Above Kelly"
        st.metric("Your Risk Level", f"{user_risk_pct}%", risk_comparison)


# Visualisation section
visualisation_container = st.container()
with (visualisation_container):
    st.header("🚀 Compounding Growth Simulation")
    st.markdown("""
    **Visualizing how your trading strategy compounds over time**  
    *The chart below shows your account growth trajectory based on the parameters you've set*
    """)

    # Present data in tabs - one for table and one for chart
    tab1, tab2, tab3, tab4 = st.tabs(["DataTable", "Chart", "Summary Table", "Summary"])
    with tab1:
        # Create DataFrame for the compound rate results
        compound_interest_result_df = pd.DataFrame()

        # Enter the loop - cycles contains periods
        list_of_possible_R_outcomes = [win_reward_R, -1]
        for simulation in range(1, 101):
            # Take start balance before entering the new cycle loop
            start_balance = starting_account_balance
            # Set the initial risk before entering the new cycle loop
            risk_per_trade = round(start_balance * user_risk_pct / 100, 0)

            for cycle in range(1, no_of_cycles+1):
                return_per_cycle = []
                # Generate list of trade outcomes per cycle
                list_of_trade_outcomes = random.choices(
                    list_of_possible_R_outcomes,
                    weights=[win_probability_pct, 100-win_probability_pct],
                    k=no_of_opportunities_per_period*no_of_periods
                )

                for period in range(1, no_of_periods+1):
                    # Work only until the account target has been reached
                    if (start_balance >= ending_account_balance) or (start_balance <= 0):
                        break
                    # Adjust risk if user adapts risk per cycle or per period
                    # in other cases or never it nothing is chosen
                    if (period == 1) and (user_risk_adj_period == "Cycle"):
                        risk_per_trade = round(start_balance * user_risk_pct / 100, 0)
                    elif user_risk_adj_period == "Period":
                        risk_per_trade = round(start_balance * user_risk_pct / 100, 0)
                    else:
                        risk_per_trade = risk_per_trade

                    # Calculations required per period
                    list_of_trade_outcomes_in_period = list_of_trade_outcomes[
                        period*no_of_opportunities_per_period-no_of_opportunities_per_period:period*no_of_opportunities_per_period]
                    real_r_return_per_period = sum(list_of_trade_outcomes_in_period)

                    no_of_wins_in_period = list_of_trade_outcomes_in_period.count(list_of_possible_R_outcomes[0])
                    no_of_loses_in_period = len(list_of_trade_outcomes_in_period) - no_of_wins_in_period
                    return_on_period = real_r_return_per_period * risk_per_trade
                    return_per_cycle.append(return_on_period)
                    tax_withheld = round(return_on_period * tax_value_pct / 100, 0) if tax_period == "Period" else 0
                    add_to_account = add_to_account_value if add_to_account_period == "Period" else 0
                    withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Period" else 0

                    # Calculations required if user choose Cycle in some cases rather than Period
                    if period == no_of_periods:
                        add_to_account = add_to_account_value if add_to_account_period == "Cycle" else add_to_account
                        withdraw_from_account = withdraw_from_account_value if withdraw_from_account_period == "Cycle" else withdraw_from_account
                        tax_withheld = sum(return_per_cycle) * tax_value_pct / 100 if tax_period == "Cycle" else tax_withheld

                    end_balance = round(start_balance + return_on_period + add_to_account - withdraw_from_account - tax_withheld, 0)

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

                    compound_interest_result_df = pd.concat([compound_interest_result_df, new_row_df], ignore_index=True)
                    compound_interest_result_df['Peak Balance'] = compound_interest_result_df.groupby('Sim')['End Balance'].cummax()
                    compound_interest_result_df['Drawdown'] = compound_interest_result_df['Peak Balance'] - compound_interest_result_df['End Balance']
                    compound_interest_result_df['Drawdown pct'] = round(
                        (compound_interest_result_df['Peak Balance'] - compound_interest_result_df['End Balance']) /
                        compound_interest_result_df['Peak Balance'] * 100, 1)

                    start_balance = end_balance

        # Show DataFrame
        # sim_to_show = st.number_input("Simulation number to show", 1, 100, 1, key="sim_no_choice")

        if "sim_to_show" not in st.session_state:
            st.session_state.sim_to_show=1

        col1a, col2a = st.columns(2)
        with col1a:
            if st.button("Previous"):
                st.session_state.sim_to_show = max(1, st.session_state.sim_to_show - 1)
        with col2a:
            if st.button("Next"):
                st.session_state.sim_to_show = min(100, st.session_state.sim_to_show + 1)

        st.write(f"Showing simulation: {st.session_state.sim_to_show}")

        # st.session_state.sim_to_show = st.number_input("Simulation number to show", 1, 100, 1)

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

    with tab2:
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
            title="Account Growth Over Time",
            xaxis_title="Period Sequence",
            yaxis_title="Account Balance ($)",
            hovermode="x unified",
            template="plotly_white",

        )
        st.plotly_chart(fig, config={"displayModeBar": False}, use_container_width=True)
        # else:
        #     st.warning("This expectancy value is not mathematically possible with positive risk:reward ratios")

    with tab3:
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
    with tab4:
        no_ruin_summary_df = summary_df[summary_df["END_Balance"] > 0]
        min_end_balance = no_ruin_summary_df["END_Balance"].min()
        max_end_balance = no_ruin_summary_df["END_Balance"].max()
        avg_end_balance = no_ruin_summary_df["END_Balance"].mean()
        risk_of_ruin_pct = len(summary_df[summary_df["END_Balance"] <= 0])
        avg_return_period = no_ruin_summary_df["AVG_Return"].mean()
        max_drawdown = no_ruin_summary_df["MAX_Drawdown"].max()
        min_drawdown = no_ruin_summary_df["MAX_Drawdown"].min()
        avg_drawdown = no_ruin_summary_df["MAX_Drawdown"].mean()

        st.metric("Minimum End Balance", f"${min_end_balance}", help="The lowest of the ending balances")
        st.metric("Maximum End Balance", f"${max_end_balance}", help="The highest of the ending balances")
        st.metric("Average End Balance", f"${avg_end_balance}", help="The average of the ending balances")
        st.metric("Risk of Ruin", f"{risk_of_ruin_pct}%", help="Chances of account blowout")
        st.metric("Average Return Per Period", f"${avg_return_period}", help="Average expected return per Period")
        st.metric("Minimum Drawdown", f"${min_drawdown}", help="The lowest of the drawdowns")
        st.metric("Maximum Drawdown", f"${max_drawdown}", help="The highest of the drawdowns")
        st.metric("Average Drawdown", f"${avg_drawdown}", help="The average of the drawdowns")


# Explanation
with st.expander("💡 How to Interpret These Results"):
    st.markdown(f"""
    Your trading strategy's performance is modeled using the **compound interest formula** adapted for trading risk:

    **Formula**: `A = P × (1 + r/n)^(n×t)`
    - **A**: End balance
    - **P**: Starting balance ({starting_account_balance:,.0f})
    - **r**: Expected return per period ({r_return_per_period:.1f}R)
    - **n**: Opportunities per period ({no_of_opportunities_per_period})
    - **t**: Total periods ({no_of_periods * no_of_cycles})

    **Key Insights**:
    - **Expectancy**: {expectancy:.2f}R per trade
    - **Kelly Criterion**: Risk {kelly_percentage:.2f}% per trade (half-Kelly: {kelly_percentage/2:.2f}%)
    - **End Balance**: {compound_interest_result_df['End Balance'].iloc[-1]:,.0f}
    - **Risk Management**: Adjust risk per {user_risk_adj_period} for balance.
    """)


# Footer
st.markdown("---")
st.caption("© 2025 ClockTrades.com • All calculations are theoretical and don't guarantee future results • "
           "Risk management is essential in trading")
