from .base_agent import Agent

class FundManagerAgent(Agent):
    def __init__(self, name, llm_client):
        super().__init__(name)
        self.llm_client = llm_client

    def execute(self, trade_decision, risk_assessment):
        """
        Gives final authorization for a trade.
        """
        # In a real implementation, the LLM would provide a more sophisticated authorization logic.

        prompt = (
            f"Given the trade decision '{trade_decision}' and the risk assessment "
            f"'{risk_assessment}', should the trade be authorized?"
        )

        authorization = self.llm_client.generate_response(prompt)

        return authorization
