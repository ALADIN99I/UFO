import pandas as pd
from src.data_ingestion import DataIngestionAgent
from src.ufo_calculators import PercentageVariationAgent, IncrementalSummationAgent, UfoChartAgent
from src.portfolio_management import PortfolioEquationAgent, EquityCurveAgent
from src.trading_agents import TraderAgent, RiskManagementAgent

def main():
    # --- 1. Data Ingestion ---
    data_ingestion_agent = DataIngestionAgent(file_path='data/sample_data.csv')
    raw_data = data_ingestion_agent.load_data()
    if raw_data is None:
        return

    # --- 2. UFO Calculation ---
    percentage_variation_agent = PercentageVariationAgent()
    variation_data = percentage_variation_agent.calculate_variation(raw_data.copy())

    incremental_summation_agent = IncrementalSummationAgent()
    incremental_sums = incremental_summation_agent.calculate_incremental_sum(variation_data)

    currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD']
    ufo_chart_agent = UfoChartAgent(currencies=currencies)
    ufo_data = ufo_chart_agent.generate_ufo_chart(incremental_sums)

    # --- 3. Portfolio Management ---
    # Example portfolio equation
    portfolio_equation = {'EURUSD': 'buy', 'USDJPY': 'sell'}
    portfolio_equation_agent = PortfolioEquationAgent(equation=portfolio_equation)

    equity_curve_agent = EquityCurveAgent()
    portfolio_equity_curve = equity_curve_agent.generate_equity_curve(
        portfolio_equation_agent.get_equation(),
        incremental_sums
    )

    # --- 4. Trading and Risk Management ---
    trader_agent = TraderAgent()
    trade_decision = trader_agent.decide_trades(ufo_data, portfolio_equity_curve)

    risk_management_agent = RiskManagementAgent(stop_loss_threshold=-0.01)
    risk_status = risk_management_agent.check_risk(portfolio_equity_curve)

    # --- 5. Output ---
    print("--- UFO Market Performance ---")
    print(ufo_data)
    print("\n--- Portfolio Equity Curve ---")
    print(portfolio_equity_curve)
    print("\n--- Trade Decision ---")
    print(trade_decision)
    print("\n--- Risk Status ---")
    print(risk_status)

if __name__ == "__main__":
    main()
