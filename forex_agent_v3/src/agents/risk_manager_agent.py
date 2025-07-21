from .base_agent import Agent

class RiskManagerAgent(Agent):
    def __init__(self, name, llm_client, stop_loss_threshold=-2.0):
        super().__init__(name, llm_client)
        self.stop_loss_threshold = stop_loss_threshold

    def execute(self, trade_decision, portfolio_equity_curve):
        """
        Assesses the risk of a trade and the overall portfolio using the LLM.
        """
        prompt = (
            f"Assess the risk of the following trade decision, considering market "
            f"volatility and the current portfolio equity curve:\n\n"
            f"Trade Decision: {trade_decision}\n"
            f"Portfolio Equity Curve: {portfolio_equity_curve.to_string()}"
        )

        risk_assessment = self.llm_client.generate_response(prompt)

        portfolio_risk = "OK"
        if not portfolio_equity_curve.empty and portfolio_equity_curve.iloc[-1] < self.stop_loss_threshold:
            portfolio_risk = "STOP_LOSS_BREACHED"

        return {
            "trade_risk_assessment": risk_assessment,
            "portfolio_risk_status": portfolio_risk
        }
