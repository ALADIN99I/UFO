from .base_agent import Agent

class MarketResearcherAgent(Agent):
    def execute(self, ufo_data, economic_events):
        """
        Analyzes the UFO data and economic events from bullish and bearish perspectives using the LLM.
        """
        ufo_data_str = ""
        for timeframe, ufo_df in ufo_data.items():
            ufo_data_str += f"--- Timeframe: {timeframe} ---\n{ufo_df.tail().to_string()}\n\n"

        economic_events_str = economic_events.to_string() if economic_events is not None and not economic_events.empty else "No upcoming economic events."

        analysis_prompt = (
            "You are a senior Forex market analyst. Based on the following UFO data across multiple timeframes, "
            "provide a comprehensive market analysis. Assess the consistency of currency strength and weakness "
            "across the timeframes to determine high-probability trading opportunities. Identify the primary market "
            "sentiment and suggest a hedged portfolio of trades that aligns with this sentiment. "
            "The portfolio should be constructed by pairing strong currencies against weak currencies.\n\n"
            f"UFO Data:\n{ufo_data_str}\n\n"
            f"Upcoming Economic Events:\n{economic_events_str}\n\n"
            "Your analysis should conclude with a clear recommendation for a portfolio of trades."
        )

        analysis = self.llm_client.generate_response(analysis_prompt)

        consensus_prompt = (
            "You are a senior market strategist. Based on the following market analysis, "
            "formulate a concrete trading plan. The plan should consist of a portfolio of trades "
            "that creates a hedged position. For each trade, specify the currency pair and direction (buy/sell)."
            "The final output should be a JSON object containing a list of trades, like this: "
            "`{'trades': [{'currency_pair': 'EURCAD', 'direction': 'Buy'}, {'currency_pair': 'GBPUSD', 'direction': 'Sell'}]}`\n\n"
            f"Market Analysis:\n{analysis}"
        )

        consensus = self.llm_client.generate_response(consensus_prompt)

        return {
            "analysis": analysis,
            "consensus": consensus
        }
