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
            "and risk appetite. The overall portfolio risk should not exceed 5% of the account balance. "
            "Portfolio risk between 3-5% is acceptable for higher probability setups. "
            "If portfolio risk exceeds 5%, the system will automatically scale down position sizes to maintain 4.5% risk. "
            "Therefore, approve trades with good analysis and favorable risk/reward ratios (>1:1), even if initial risk is high. "
            "Only reject trades if risk/reward ratios are very unfavorable (<1:1) or if there are fundamental flaws in the analysis.\n\n"
            f"Trade Plan:\n{trade_decision}\n\n"
            f"Risk Assessment:\n{risk_assessment}"
        )

        authorization = self.llm_client.generate_response(prompt)
        return authorization
