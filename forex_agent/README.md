# Agentic Framework for Intraday Forex Trading

This project is an implementation of an agentic framework for intraday Forex trading based on the UFO market performance methodology.

## Project Structure

- `data/`: Contains sample data for the simulation.
- `src/`: Contains the Python source code for the agents.
- `main.py`: The main script to run the trading simulation.

## How to Run

1. **Install dependencies:**
   ```bash
   pip install pandas
   ```

2. **Run the simulation:**
   ```bash
   python main.py
   ```

## Methodology

The framework is based on the following concepts:

- **UFO Market Performance:** A proprietary calculation to determine currency strength and weakness.
- **Portfolio Monitoring:** A method of creating a "synthetic asset" to track overall portfolio profitability.
- **Agent-Based System:** The framework is composed of specialized agents for data ingestion, calculation, decision-making, and risk management.
