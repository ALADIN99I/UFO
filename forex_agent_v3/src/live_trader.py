import time
import pandas as pd
try:
    import MetaTrader5 as mt5
except ImportError:
    from . import mock_metatrader5 as mt5
from .data_collector import MT5DataCollector
from .agents.data_analyst_agent import DataAnalystAgent
from .agents.market_researcher_agent import MarketResearcherAgent
from .agents.trader_agent import TraderAgent
from .agents.risk_manager_agent import RiskManagerAgent
from .agents.fund_manager_agent import FundManagerAgent
from .communication import CommunicationBus
from .ufo_calculator import UfoCalculator
from .llm.llm_client import LLMClient

class LiveTrader:
    def __init__(self, config):
        self.config = config
        self.llm_client = LLMClient(api_key=config['openrouter']['api_key'])

        mt5_collector = MT5DataCollector(
            login=config['mt5']['login'],
            password=config['mt5']['password'],
            server=config['mt5']['server'],
            path=config['mt5']['path']
        )

        self.agents = {
            "data_analyst": DataAnalystAgent("DataAnalyst", mt5_collector, config['fmp']['api_key']),
            "researcher": MarketResearcherAgent("MarketResearcher", self.llm_client),
            "trader": TraderAgent("Trader", self.llm_client, mt5_collector),
            "risk_manager": RiskManagerAgent("RiskManager", self.llm_client, mt5_collector),
            "fund_manager": FundManagerAgent("FundManager", self.llm_client)
        }

        self.communication_bus = CommunicationBus()
        self.ufo_calculator = UfoCalculator(config['trading']['currencies'].split(','))

    def run(self):
        """
        Runs the live trading loop.
        """
        while True:
            # 1. Data Collection
            # In a real scenario, you'd fetch data for all 28 crosses.
            # For this simulation, we'll use a single symbol.
            price_data = self.agents['data_analyst'].execute({
                'source': 'mt5',
                'symbol': 'EURUSD',
                'timeframe': mt5.TIMEFRAME_M5,
                'num_bars': 100
            })

            if price_data is None:
                print("Could not fetch price data. Retrying in 60 seconds...")
                time.sleep(60)
                continue

            # 2. UFO Calculation
            variation_data = self.ufo_calculator.calculate_percentage_variation(price_data)
            incremental_sums = self.ufo_calculator.calculate_incremental_sum(variation_data)
            ufo_data = self.ufo_calculator.generate_ufo_data(incremental_sums)

            # 3. Agentic Workflow
            economic_events = self.agents['data_analyst'].execute({'source': 'economic_calendar'})
            research_result = self.agents['researcher'].execute(ufo_data, economic_events)
            trade_decision = self.agents['trader'].execute(research_result['consensus'])

            risk_assessment = self.agents['risk_manager'].execute(trade_decision)
            authorization = self.agents['fund_manager'].execute(trade_decision, risk_assessment)

            # 4. Output
            print("\n--- Live Trading Cycle ---")
            print(f"Timestamp: {pd.Timestamp.now()}")
            print(f"Research Consensus: {research_result['consensus']}")
            print(f"Trade Decision: {trade_decision}")
            print(f"Risk Assessment: {risk_assessment}")
            print(f"Final Authorization: {authorization}")

            print("\nWaiting for the next trading cycle (5 minutes)...")
            time.sleep(300) # Wait for 5 minutes
