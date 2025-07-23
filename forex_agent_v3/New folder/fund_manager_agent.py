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
            "*** CRITICAL DIRECTIVE: The account owner has EXPLICITLY set their risk tolerance to 9.4% per trade. "
            "This is a FIRM requirement and MUST be respected without question. You are FORBIDDEN from "
            "rejecting trades based on risk percentage or lot size concerns when they align with the 9.4% mandate. "
            "ONLY reject trades for: (1) Invalid technical setups, (2) Missing required data, (3) Market closure, "
            "or (4) Clear fundamental contradictions. Risk/reward ratios and portfolio sustainability concerns "
            "are NOT valid rejection reasons when the trade uses the specified 9.4% risk level. ***\n\n"
            f"Trade Plan:\n{trade_decision}\n\n"
            f"Risk Assessment:\n{risk_assessment}"
        )

        authorization = self.llm_client.generate_response(prompt)
        return authorization
