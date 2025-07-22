from .base_agent import Agent

class FundManagerAgent(Agent):
    def execute(self, trade_decision, risk_assessment):
        """
        Gives final authorization for a trade using the LLM.
        """
        prompt = (
            "You are the Fund Manager. Based on the provided trade plan and risk assessment, "
            "make a final decision to 'APPROVE' or 'REJECT' the trade. Provide a concise "
            "justification for your decision, considering the overall portfolio strategy "
            "and risk appetite.\n\n"
            f"Trade Plan:\n{trade_decision}\n\n"
            f"Risk Assessment:\n{risk_assessment}"
        )

        authorization = self.llm_client.generate_response(prompt)
        return authorization
