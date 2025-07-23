from .base_agent import Agent
from ..portfolio_manager import PortfolioManager

class RiskManagerAgent(Agent):
    def __init__(self, name, llm_client, mt5_connection, stop_loss_threshold=-2.0):
        super().__init__(name, llm_client)
        self.portfolio_manager = PortfolioManager(mt5_connection)
        self.stop_loss_threshold = stop_loss_threshold

    def execute(self, trade_decision):
        """
        Assesses the risk of a trade and the overall portfolio using the LLM.
        """
        equity_curve = self.portfolio_manager.calculate_equity_curve()

        prompt = (
            "You are a senior risk analyst. Assess the risk of the following trade plan. "
            "Consider market volatility, the provided equity curve, and the overall risk "
            "profile of the portfolio. Provide a risk score (1-5) and a detailed "
            "justification for your assessment.\n\n"
            f"Trade Plan:\n{trade_decision}\n\n"
            f"Portfolio Equity Curve:\n{equity_curve.to_string() if equity_curve is not None else 'N/A'}"
        )

        risk_assessment = self.llm_client.generate_response(prompt)

        portfolio_risk = "OK"
        if equity_curve is not None and not equity_curve.empty:
            account_info = self.portfolio_manager.get_account_info()
            if account_info:
                current_equity = equity_curve['equity'].iloc[-1]
                initial_balance = account_info.balance
                drawdown = (current_equity - initial_balance) / initial_balance * 100
                if drawdown < self.stop_loss_threshold:
                    portfolio_risk = "STOP_LOSS_BREACHED"
                    self.portfolio_manager.close_all_trades()

        return {
            "trade_risk_assessment": risk_assessment,
            "portfolio_risk_status": portfolio_risk
        }
