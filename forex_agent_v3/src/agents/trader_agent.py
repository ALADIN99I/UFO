from .base_agent import Agent
from ..portfolio_manager import PortfolioManager

class TraderAgent(Agent):
    def __init__(self, name, llm_client, mt5_connection):
        super().__init__(name, llm_client)
        self.portfolio_manager = PortfolioManager(mt5_connection)

    def execute(self, research_consensus, open_positions):
        """
        Makes a trading decision based on the research consensus and open positions using the LLM.
        """
        account_info = self.portfolio_manager.get_account_info()
        balance = account_info.balance if account_info else 10000  # Default to 10k if info not available

        open_positions_str = open_positions.to_string() if not open_positions.empty else "No open positions."

        prompt = (
            "You are a professional Forex trader. Based on the following multi-timeframe research consensus and "
            "the current open positions, formulate a precise and actionable trade plan. "
            "Your plan should synthesize insights from all available timeframes to ensure it reflects the 'bigger picture'. "
            "This may involve opening new trades, reinforcing existing positions (e.g., by adding to the lot size), or closing positions.\n\n"
            "The trade plan should be a list of actions in a JSON object, with each action having the following structure: "
            "`{'action': 'new_trade'/'adjust_trade'/'close_trade', 'trade_id': <optional>, 'currency_pair': 'EURUSD', 'direction': 'SELL', 'entry_price': 1.0800, 'stop_loss': 1.0850, 'take_profit': 1.0650, 'lot_size': 0.40}`.\n\n"
            f"The lot size should be calculated for a ${balance} account with a 1-3% risk tolerance per trade/portfolio.\n\n"
            f"Research Consensus:\n{research_consensus}\n\n"
            f"Current Open Positions:\n{open_positions_str}"
        )

        trade_decision_str = self.llm_client.generate_response(prompt)

        if not isinstance(trade_decision_str, str) or not trade_decision_str.strip():
            trade_decision_str = "{\"trades\": []}"
            print("Warning: TraderAgent LLM did not return a valid trade decision string.")

        print(f"LLM Trade Decision:\n{trade_decision_str}")
        return trade_decision_str
