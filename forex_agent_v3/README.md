# Agentic Framework for Intraday Forex Trading (v3)

This project is a sophisticated, agent-based system for intraday Forex trading. It leverages a proprietary UFO algorithm, a multi-agent architecture, and live data integration to make informed trading decisions.

## Project Structure

- `config/`: Configuration files for API keys and trading parameters.
- `data/`: (Not used in live trading) For storing historical data for backtesting.
- `src/`: Python source code.
  - `agents/`: Specialized agent classes.
  - `llm/`: LLM integration.
  - `data_collector.py`: Data collection from MT5 and Finnhub.
  - `ufo_calculator.py`: UFO algorithm implementation.
  - `live_trader.py`: Main live trading loop.
- `main.py`: Entry point to start the live trading bot.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install pandas MetaTrader5 finnhub-python openai
    ```
    *(Note: `MetaTrader5` is Windows-only. A mock version is included for development on other platforms.)*

2.  **Configure the system:**
    - Fill in your API keys and MT5 credentials in `config/config.ini`.

3.  **Run the live trading bot:**
    ```bash
    python main.py
    ```

## Core Components

- **Live Data Integration:** Fetches real-time price data from MetaTrader 5 and economic news from Finnhub.
- **UFO Algorithm:** Mathematically derives currency strength and weakness.
- **Multi-Agent System:** A team of AI agents (Data Analyst, Researcher, Trader, Risk Manager, Fund Manager) that collaborate to make decisions.
- **LLM-Powered Reasoning:** Uses a Large Language Model (via OpenRouter) for advanced analysis and strategic decision-making.
- **Live Trading Loop:** Continuously monitors the market and executes the trading strategy.
