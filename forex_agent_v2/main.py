import pandas as pd
from src.agents.data_analyst_agent import DataAnalystAgent
from src.agents.market_researcher_agent import MarketResearcherAgent
from src.agents.trader_agent import TraderAgent
from src.agents.risk_manager_agent import RiskManagerAgent
from src.agents.fund_manager_agent import FundManagerAgent
from src.communication import CommunicationBus
from src.ufo_calculator import UfoCalculator
from src.backtester import Backtester
from src.llm.mock_llm_client import MockLLMClient

def main():
    # --- Configuration ---
    mt5_credentials = {
        "mt5_path": "path/to/mt5/terminal.exe",
        "username": "your_username",
        "password": "your_password",
        "server": "your_server"
    }
    finnhub_api_key = "your_finnhub_api_key"
    currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD']

    # --- Initialize Components ---
    llm_client = MockLLMClient(model_name='deepseek/deepseek-chat-v3-0324:free')

    agents = {
        "data_analyst": DataAnalystAgent("DataAnalyst", mt5_credentials, finnhub_api_key),
        "researcher": MarketResearcherAgent("MarketResearcher", llm_client),
        "trader": TraderAgent("Trader", llm_client),
        "risk_manager": RiskManagerAgent("RiskManager", llm_client),
        "fund_manager": FundManagerAgent("FundManager", llm_client)
    }

    communication_bus = CommunicationBus()
    ufo_calculator = UfoCalculator(currencies)
    backtester = Backtester(agents, communication_bus, ufo_calculator)

    # --- Load Historical Data ---
    # In a real scenario, this data would be fetched by the DataAnalystAgent.
    # For this simulation, we'll create a dummy dataframe.
    historical_data = pd.DataFrame({
        'time': pd.to_datetime(['2023-01-02 00:00:00', '2023-01-02 00:05:00', '2023-01-02 00:10:00']),
        'EURUSD': [1.0655, 1.0660, 1.0665],
        'GBPUSD': [1.2050, 1.2055, 1.2060],
        'USDJPY': [130.80, 130.85, 130.90]
    })


    # --- Run Backtesting ---
    backtester.run(historical_data)

if __name__ == "__main__":
    main()
