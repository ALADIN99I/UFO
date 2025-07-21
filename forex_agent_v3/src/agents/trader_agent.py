from .base_agent import Agent

class TraderAgent(Agent):
    def execute(self, research_consensus):
        """
        Makes a trading decision based on the research consensus using the LLM.
        """
        prompt = (
            f"Based on the following research consensus, formulate a specific trade "
            f"decision (buy/sell, currency pair, lot size, entry/exit points):\n\n"
            f"Consensus: {research_consensus}"
        )

        trade_decision = self.llm_client.generate_response(prompt)
        return trade_decision
