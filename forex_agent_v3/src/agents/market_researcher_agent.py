from .base_agent import Agent

class MarketResearcherAgent(Agent):
    def execute(self, ufo_data, economic_events):
        """
        Analyzes the UFO data and economic events from bullish and bearish perspectives using the LLM.
        """
        strongest_currency = ufo_data.iloc[-1].idxmax()
        weakest_currency = ufo_data.iloc[-1].idxmin()

        bullish_prompt = (
            f"You are a bullish Forex market analyst. Given the following UFO data, which shows "
            f"{strongest_currency} as the strongest currency, and the upcoming economic events, "
            f"provide a detailed bullish analysis. Focus on the potential for {strongest_currency} "
            f"to continue its rally.\n\nUFO Data:\n{ufo_data.tail().to_string()}\n\n"
            f"Economic Events:\n{economic_events.to_string()}"
        )

        bearish_prompt = (
            f"You are a bearish Forex market analyst. Given the following UFO data, which shows "
            f"{weakest_currency} as the weakest currency, and the upcoming economic events, "
            f"provide a detailed bearish analysis. Focus on the potential for {weakest_currency} "
            f"to continue its decline.\n\nUFO Data:\n{ufo_data.tail().to_string()}\n\n"
            f"Economic Events:\n{economic_events.to_string()}"
        )

        bullish_perspective = self.llm_client.generate_response(bullish_prompt)
        bearish_perspective = self.llm_client.generate_response(bearish_prompt)

        consensus_prompt = (
            "You are a senior market strategist. Synthesize the following bullish and bearish "
            "perspectives into a single, actionable trading recommendation. Provide a clear "
            "currency pair to trade, the direction (buy/sell), and a brief justification.\n\n"
            f"Bullish Analysis:\n{bullish_perspective}\n\n"
            f"Bearish Analysis:\n{bearish_perspective}"
        )

        consensus = self.llm_client.generate_response(consensus_prompt)

        return {
            "bullish": bullish_perspective,
            "bearish": bearish_perspective,
            "consensus": consensus
        }
