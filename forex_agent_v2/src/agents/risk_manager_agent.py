from .base_agent import Agent

class RiskManagerAgent(Agent):
    def __init__(self, name, llm_client, stop_loss_threshold=-2.0):
        super().__init__(name)
        self.llm_client = llm_client
        self.stop_loss_threshold = stop_loss_threshold

    def execute(self, trade_decision, portfolio_equity_curve):
        """
        Assesses the risk of a trade and the overall portfolio.
        """
        # In a real implementation, the LLM would provide a more nuanced risk assessment.

        risk_assessment = self.llm_client.generate_response(
            f"Assess the risk of the following trade: {trade_decision}"
        )

        portfolio_risk = "OK"
        if not portfolio_equity_curve.empty and portfolio_equity_curve.iloc[-1] < self.stop_loss_threshold:
            portfolio_risk = "STOP_LOSS_BREACHED"

        return {
            "trade_risk_assessment": risk_assessment,
            "portfolio_risk_status": portfolio_risk
        }
