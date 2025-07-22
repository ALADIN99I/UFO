from .base_agent import Agent

class TraderAgent(Agent):
    def __init__(self, name, llm_client):
        super().__init__(name)
        self.llm_client = llm_client

    def execute(self, research_consensus):
        """
        Makes a trading decision based on the research consensus.
        """
        # In a real implementation, the LLM would help determine the trade details.
        # Here, we'll just formalize the decision.

        prompt = f"Based on the consensus '{research_consensus}', what is the optimal trade?"
        trade_decision = self.llm_client.generate_response(prompt)

        return trade_decision
