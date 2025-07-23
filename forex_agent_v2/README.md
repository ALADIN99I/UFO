# Agentic Framework for Intraday Forex Trading (v2)

This project is an advanced implementation of an agentic framework for intraday Forex trading, based on the UFO market performance methodology and leveraging a multi-agent architecture with LLM integration.

## Project Structure

- `config/`: Contains configuration files.
- `data/`: Contains sample data for backtesting.
- `src/`: Contains the Python source code for the agents and framework components.
  - `agents/`: Contains the specialized agent classes.
  - `llm/`: Contains the LLM client (mocked for this simulation).
- `main.py`: The main script to run the backtesting simulation.

## How to Run

1. **Install dependencies:**
   ```bash
   pip install pandas
   ```

2. **Configure the system:**
   - Add your API keys and other settings to `config/config.ini`.

3. **Run the simulation:**
   ```bash
   python main.py
   ```

## Methodology

This framework is based on a sophisticated, multi-layered approach:

- **UFO Algorithm:** A proprietary method for calculating intrinsic currency strength and weakness.
- **Portfolio Hedging:** A strategy focused on the profitability of a "synthetic asset" composed of multiple currency crosses.
- **Multi-Agent System:** A collaborative architecture of specialized agents for data analysis, research, trading, and risk management.
- **LLM Integration:** The use of Large Language Models (simulated in this version) for advanced reasoning and decision-making.
- **Backtesting:** A robust environment for validating the trading strategy against historical data.
