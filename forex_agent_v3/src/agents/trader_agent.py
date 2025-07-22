from .base_agent import Agent
from ..trade_executor import TradeExecutor
try:
    import MetaTrader5 as mt5
except ImportError:
    from .. import mock_metatrader5 as mt5

class TraderAgent(Agent):
    def __init__(self, name, llm_client, mt5_connection):
        super().__init__(name, llm_client)
        self.trade_executor = TradeExecutor(mt5_connection)

    def execute(self, research_consensus):
        """
        Makes a trading decision based on the research consensus using the LLM,
        and then executes the trade.
        """
        prompt = (
            "You are a professional Forex trader. Based on the following research consensus, "
            "formulate a precise and actionable trade plan. Specify the currency pair, "
            "trade direction (buy/sell), entry price, stop-loss, take-profit, and lot size "
            "for a $10,000 account with a 2% risk tolerance.\n\n"
            f"Research Consensus:\n{research_consensus}"
        )

        trade_decision_str = self.llm_client.generate_response(prompt)

        # In a real implementation, you would parse the trade_decision_str
        # to get the trade parameters.
        # For this simulation, we'll print the decision and use placeholder values.
        print(f"LLM Trade Decision:\n{trade_decision_str}")

        if self.trade_executor.mt5.connect():
            tick = mt5.symbol_info_tick("EURUSD")
            if tick:
                trade_params = {
                    "symbol": "EURUSD",
                    "trade_type": mt5.ORDER_TYPE_BUY,
                    "volume": 0.1,
                    "price": tick.ask,
                    "sl": tick.ask - 0.001,
                    "tp": tick.ask + 0.002,
                    "comment": "LLM_trade"
                }
                trade_result = self.trade_executor.execute_trade(**trade_params)
                return trade_result

        return None
        # This can be enabled once the system is fully tested.
        # trade_result = self.trade_executor.execute_trade(**trade_params)

        return trade_decision_str
