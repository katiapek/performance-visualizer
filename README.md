# Trading Strategy Performance Visualizer

A Monte Carlo simulation tool that models 100 possible futures for a trading strategy based on win rate, risk/reward ratio, and position sizing. Built with Streamlit and Plotly.

**[Live Demo](https://performance-visualizer.marketsmanners.com/)**

## Features

- **Monte Carlo simulation** — generates 100 randomized equity curves based on your strategy parameters
- **Expectancy & Kelly Criterion** — real-time calculation of expected return and optimal position sizing
- **Equity curve visualization** — interactive Plotly chart showing the full range of possible outcomes
- **Drawdown analysis** — tracks maximum drawdown across all simulated paths
- **Configurable parameters** — win probability, reward-to-risk ratio, number of trades, risk per trade

## Tech Stack

- **Streamlit** — interactive web application
- **Plotly** — equity curve and distribution charts
- **pandas** — simulation data handling
- **Docker** — containerized deployment

## Run Locally

```bash
git clone https://github.com/katiapek/performance-visualizer.git
cd performance-visualizer
pip install streamlit plotly pandas
streamlit run PerformanceVisualizer.py
```

## Related Projects

| Project | Description |
|---------|-------------|
| [Expectancy Calculator](https://github.com/katiapek/expectancy-calculator) | Expectancy and Kelly Criterion calculator with analysis charts |
| [Compounding Simulator](https://github.com/katiapek/compounding-simulator) | Long-term growth simulation with compounding and risk management |
| [Financial Analysis Terminal](https://github.com/katiapek/financial-analysis-terminal) | Quantitative analytics pipeline for futures markets |

## License

MIT
