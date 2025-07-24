import time
import pandas as pd
import re
import json
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
from .trade_executor import TradeExecutor

class LiveTrader:
    def __init__(self, config):
        self.config = config
        self.llm_client = LLMClient(api_key=config['openrouter']['api_key'])

        self.mt5_collector = MT5DataCollector(
            login=config['mt5']['login'],
            password=config['mt5']['password'],
            server=config['mt5']['server'],
            path=config['mt5']['path']
        )

        self.trade_executor = TradeExecutor(self.mt5_collector)

        self.agents = {
            "data_analyst": DataAnalystAgent("DataAnalyst", self.mt5_collector),
            "researcher": MarketResearcherAgent("MarketResearcher", self.llm_client),
            "trader": TraderAgent("Trader", self.llm_client, self.mt5_collector),
            "risk_manager": RiskManagerAgent("RiskManager", self.llm_client, self.mt5_collector),
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
            base_symbol = 'EURUSD'
            symbol_suffix = self.config['mt5'].get('symbol_suffix', '')
            symbol_with_suffix = base_symbol + symbol_suffix
            timeframes = [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1]

            price_data_dict = {}
            timeframe_bars = {
                mt5.TIMEFRAME_M5: 100,
                mt5.TIMEFRAME_M15: 100,
                mt5.TIMEFRAME_H1: 120,
                mt5.TIMEFRAME_H4: 120,
                mt5.TIMEFRAME_D1: 100
            }
            for timeframe, num_bars in timeframe_bars.items():
                data = self.agents['data_analyst'].execute({
                    'source': 'mt5',
                    'symbol': symbol_with_suffix,
                    'timeframes': [timeframe],
                    'num_bars': num_bars
                })
                if data:
                    price_data_dict.update(data)

            if not price_data_dict:
                print("Could not fetch price data. Retrying in 60 seconds...")
                time.sleep(60)
                continue

            # 2. UFO Calculation
            incremental_sums_dict = {}
            for timeframe, price_data in price_data_dict.items():
                variation_data = self.ufo_calculator.calculate_percentage_variation(price_data)
                incremental_sums_dict[timeframe] = self.ufo_calculator.calculate_incremental_sum(variation_data)

            ufo_data = self.ufo_calculator.generate_ufo_data(incremental_sums_dict)

            # 3. Agentic Workflow
            economic_events = self.agents['data_analyst'].execute({'source': 'economic_calendar'})
            open_positions = self.agents['risk_manager'].portfolio_manager.get_positions()
            research_result = self.agents['researcher'].execute(ufo_data, economic_events)
            trade_decision_str = self.agents['trader'].execute(research_result['consensus'], open_positions)

            risk_assessment = self.agents['risk_manager'].execute(trade_decision_str)

            if risk_assessment['portfolio_risk_status'] == "STOP_LOSS_BREACHED":
                print("!!! EQUITY STOP LOSS BREACHED. CEASING ALL TRADING. !!!")
                break

            authorization = self.agents['fund_manager'].execute(trade_decision_str, risk_assessment)

            # 4. Output
            print("\n--- Live Trading Cycle ---")
            print(f"Timestamp: {pd.Timestamp.now()}")
            print(f"Research Consensus: {research_result['consensus']}")
            print(f"Trade Decision: {trade_decision_str}")
            print(f"Risk Assessment: {risk_assessment}")
            print(f"Final Authorization: {authorization}")

            # 5. Trade Execution
            if "APPROVE" in authorization.upper():
                try:
                    json_match = re.search(r'{.*}', trade_decision_str, re.DOTALL)
                    if not json_match:
                        print("No JSON object found in the LLM decision.")
                        continue

                    parsed_data = json.loads(json_match.group(0))
                    for action in parsed_data.get('actions', []):
                        action_type = action.get('action')
                        if action_type == 'new_trade':
                            # ... (validation and processing logic for new trade)
                            self.trade_executor.execute_trade(
                                symbol=action['symbol'],
                                trade_type=action['trade_type'],
                                volume=action['volume'],
                                price=action['price'],
                                sl=action['sl'],
                                tp=action['tp'],
                                comment=action.get('comment', '')
                            )
                        elif action_type == 'adjust_trade':
                            # Placeholder for adjust_trade logic
                            print(f"Adjust trade action not yet implemented: {action}")
                        elif action_type == 'close_trade':
                            self.trade_executor.close_trade(action['trade_id'])

                except Exception as e:
                    print(f"Error during trade execution: {e}")

            self.check_profit_targets()
            self.check_research_contradiction(research_result['consensus'])

            print("\nWaiting for the next trading cycle (5 minutes)...")
            time.sleep(300)

    def check_profit_targets(self):
        """
        Checks if any open positions have reached their take profit level.
        """
        positions = self.trade_executor.mt5_connection.positions_get()
        if positions is None:
            return

        for position in positions:
            if position.tp > 0:
                if position.type == mt5.ORDER_TYPE_BUY and position.price_current >= position.tp:
                    self.trade_executor.close_trade(position.ticket)
                elif position.type == mt5.ORDER_TYPE_SELL and position.price_current <= position.tp:
                    self.trade_executor.close_trade(position.ticket)

    def check_research_contradiction(self, research_consensus):
        """
        Checks if the research consensus contradicts any open positions.
        """
        positions = self.trade_executor.mt5_connection.positions_get()
        if positions is None:
            return

        for position in positions:
            # This is a simplified example. A more sophisticated implementation would
            # involve a more detailed analysis of the research consensus.
            if "SELL" in research_consensus and position.type == mt5.ORDER_TYPE_BUY:
                self.trade_executor.close_trade(position.ticket)
            elif "BUY" in research_consensus and position.type == mt5.ORDER_TYPE_SELL:
                self.trade_executor.close_trade(position.ticket)
