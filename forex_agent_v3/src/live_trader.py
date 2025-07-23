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
            trade_decision_str = self.agents['trader'].execute(research_result['consensus'])

            risk_assessment = self.agents['risk_manager'].execute(trade_decision_str)
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
                    try:
                        # Extract the JSON part of the string
                        json_match = re.search(r'{.*}', trade_decision_str, re.DOTALL)
                        if not json_match:
                            print("No JSON object found in the LLM decision.")
                            continue

                        trade_decision_json_str = json_match.group(0)
                        parsed_data = json.loads(trade_decision_json_str)

                        # Validate required fields
                        required_keys = ['currency_pair', 'direction', 'stop_loss', 'take_profit', 'lot_size']
                        if not all(key in parsed_data for key in required_keys):
                            print("Missing one or more required keys in the JSON decision.")
                            continue

                        # Process and use parsed data
                        base_symbol = parsed_data['currency_pair'].replace("/", "")
                        symbol_suffix = self.config['mt5'].get('symbol_suffix', '')
                        print(f"Read symbol_suffix from config: '{symbol_suffix}'")
                        symbol_to_trade = base_symbol + symbol_suffix
                        print(f"Constructed symbol for trade: {symbol_to_trade}")

                        direction_str = parsed_data['direction'].upper()
                        lot_size = float(parsed_data['lot_size'])
                        sl_price = float(parsed_data['stop_loss'])
                        final_tp_price = float(parsed_data['take_profit'])

                    except json.JSONDecodeError:
                        print("Failed to decode JSON from LLM decision.")
                        continue
                    except KeyError as e:
                        print(f"Missing key in JSON object: {e}")
                        continue

                    mt5_trade_type = mt5.ORDER_TYPE_SELL if "SELL" in direction_str else mt5.ORDER_TYPE_BUY

                    if self.mt5_collector.connect():
                        tick = mt5.symbol_info_tick(symbol_to_trade)
                        if tick:
                            price = tick.ask if mt5_trade_type == mt5.ORDER_TYPE_BUY else tick.bid
                            self.trade_executor.execute_trade(
                                symbol=symbol_to_trade,
                                trade_type=mt5_trade_type,
                                volume=lot_size,
                                price=price,
                                sl=sl_price,
                                tp=final_tp_price,
                                comment="LLM_trade_v3"
                            )
                        else:
                            print(f"Could not get tick for {symbol_to_trade}")
                        self.mt5_collector.disconnect()

                except Exception as e:
                    print(f"Error during trade execution: {e}")

            print("\nWaiting for the next trading cycle (5 minutes)...")
            time.sleep(300)
