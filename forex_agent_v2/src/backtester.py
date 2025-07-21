import pandas as pd

class Backtester:
    def __init__(self, agents, communication_bus, ufo_calculator):
        self.agents = agents
        self.communication_bus = communication_bus
        self.ufo_calculator = ufo_calculator

    def run(self, historical_data):
        """
        Runs the backtesting simulation.
        """
        # For this simulation, we'll process the data in a single pass.
        # A more realistic backtester would loop through the data bar by bar.

        # 1. UFO Calculation
        variation_data = self.ufo_calculator.calculate_percentage_variation(historical_data)
        incremental_sums = self.ufo_calculator.calculate_incremental_sum(variation_data)
        ufo_data = self.ufo_calculator.generate_ufo_data(incremental_sums)

        # 2. Agent Execution
        researcher = self.agents['researcher']
        trader = self.agents['trader']
        risk_manager = self.agents['risk_manager']
        fund_manager = self.agents['fund_manager']

        # Market Research
        research_result = researcher.execute(ufo_data)
        self.communication_bus.post_message('researcher', 'trader', research_result['consensus'])

        # Trading Decision
        trade_consensus = self.communication_bus.get_messages('trader')[-1]['message']
        trade_decision = trader.execute(trade_consensus)
        self.communication_bus.post_message('trader', 'risk_manager', trade_decision)

        # Risk Management
        trade_to_assess = self.communication_bus.get_messages('risk_manager')[-1]['message']
        # In a real backtest, the equity curve would be dynamic. Here, we use a placeholder.
        dummy_equity_curve = pd.Series([0, 1, 2, 1, 3])
        risk_assessment = risk_manager.execute(trade_to_assess, dummy_equity_curve)
        self.communication_bus.post_message('risk_manager', 'fund_manager', risk_assessment)

        # Fund Management
        final_assessment = self.communication_bus.get_messages('fund_manager')[-1]['message']
        authorization = fund_manager.execute(trade_decision, final_assessment)

        # 3. Final Output
        print("--- Backtesting Results ---")
        print(f"Research Consensus: {research_result['consensus']}")
        print(f"Trade Decision: {trade_decision}")
        print(f"Risk Assessment: {risk_assessment}")
        print(f"Final Authorization: {authorization}")
