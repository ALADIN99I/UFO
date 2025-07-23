import time
import pandas as pd
import re
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
                    parsed_data = {}

                    print(f"LLM Raw Output for Parsing:\n{trade_decision_str}")

                    match_pair = re.search(r"Currency Pair:\s*([A-Z]{3}/[A-Z]{3})", trade_decision_str, re.IGNORECASE)
                    if not match_pair:
                        match_pair = re.search(r"([A-Z]{3}/[A-Z]{3})", trade_decision_str, re.IGNORECASE)

                    if match_pair:
                        base_symbol = match_pair.group(1).replace("/", "")
                        symbol_suffix = self.config['mt5'].get('symbol_suffix', '')
                        print(f"Read symbol_suffix from config: '{symbol_suffix}'")
                        parsed_data['symbol'] = base_symbol + symbol_suffix
                        print(f"Appended broker suffix: {parsed_data['symbol']}")
                    else:
                        print("Could not parse currency pair from LLM decision. Skipping trade execution.")
                        continue

                    match_direction = re.search(r"Direction:\s*(Short|Sell|Buy|Long)", trade_decision_str, re.IGNORECASE)
                    if not match_direction:
                        match_direction = re.search(r"(Short|Sell|Buy|Long)", trade_decision_str, re.IGNORECASE)
                    if match_direction:
                        parsed_data['direction'] = match_direction.group(1).upper()
                    else:
                        print("Could not parse trade direction from LLM decision. Skipping trade execution.")
                        continue

                    print(f"Attempting to parse lot size from: {trade_decision_str}")
                    regex_pattern = r"([\d\.]+)\s*(lots|mini lots|standard lots)"
                    print(f"Using regex for lot size: {regex_pattern}")
                    match_lot_size = re.search(regex_pattern, trade_decision_str, re.IGNORECASE)

                    if match_lot_size:
                        print(f"Lot size match found: {match_lot_size.groups()}")
                        lot_value = float(match_lot_size.group(1))
                        unit = match_lot_size.group(2).lower()
                        if "mini" in unit:
                            parsed_data['lot_size'] = lot_value / 10
                        elif "micro" in unit:
                            parsed_data['lot_size'] = lot_value / 100
                        else:
                            parsed_data['lot_size'] = lot_value
                        print(f"Parsed lot size: {parsed_data['lot_size']}")
                    else:
                        print("Could not parse lot size from LLM decision. Skipping trade execution.")
                        continue

                    print(f"Attempting to parse SL from: {trade_decision_str}")
                    regex_pattern = r"-\s*\*\*Stop-?\s?Loss\s?\(SL\):\*\*\s*([\d\.]+)"
                    print(f"Using regex for SL: {regex_pattern}")
                    match_sl = re.search(regex_pattern, trade_decision_str, re.IGNORECASE)
                    if match_sl:
                        print(f"SL match found: {match_sl.groups()}")
                        parsed_data['sl'] = float(match_sl.group(1))
                        print(f"Parsed SL: {parsed_data['sl']}")
                    else:
                        print("Could not parse SL from LLM decision. Skipping trade execution.")
                        continue

                    match_tp = re.search(r"TP1\s*([\d\.]+)", trade_decision_str)
                    if not match_tp:
                        match_tp = re.search(r"Take-Profit \(TP\):\s*([\d\.]+)", trade_decision_str)
                    if match_tp:
                        parsed_data['tp'] = float(match_tp.group(1))
                    else:
                        print("Could not parse TP from LLM decision. Skipping trade execution.")
                        continue

                    symbol_to_trade = parsed_data['symbol']
                    direction_str = parsed_data['direction']
                    lot_size = parsed_data['lot_size']
                    sl_price = parsed_data['sl']
                    final_tp_price = parsed_data['tp']

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
