from .base_agent import Agent

class FundManagerAgent(Agent):
    def execute(self, trade_decision, risk_assessment):
        """
        Gives final authorization for a trade using the LLM.
        """
        prompt = (
            f"Given the following trade decision and risk assessment, provide a final "
            f"authorization (approved/rejected) and a brief justification:\n\n"
            f"Trade Decision: {trade_decision}\n"
            f"Risk Assessment: {risk_assessment}"
        )

        authorization = self.llm_client.generate_response(prompt)
        return authorization
