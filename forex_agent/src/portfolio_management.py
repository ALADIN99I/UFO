import pandas as pd

class PortfolioEquationAgent:
    def __init__(self, equation):
        """
        equation: a dictionary representing the portfolio equation.
                  e.g., {'EURCAD': 'buy', 'GBPUSD': 'sell'}
        """
        self.equation = equation

    def get_equation(self):
        return self.equation

class EquityCurveAgent:
    def generate_equity_curve(self, portfolio_equation, incremental_sums):
        """
        Generates the equity curve for the synthetic portfolio.
        """
        equity_curve = pd.Series(0, index=incremental_sums.index)
        for cross, direction in portfolio_equation.items():
            if cross in incremental_sums.columns:
                if direction == 'buy':
                    equity_curve += incremental_sums[cross]
                else:
                    equity_curve -= incremental_sums[cross]
        return equity_curve
