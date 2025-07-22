from .base_agent import Agent

class MarketResearcherAgent(Agent):
    def execute(self, ufo_data, economic_events=None):
        """
        Analyzes the UFO data and economic events from bullish and bearish perspectives using the LLM.
        """
        strongest_currency = ufo_data.iloc[-1].idxmax()
        weakest_currency = ufo_data.iloc[-1].idxmin()

        bullish_prompt = (
            f"You are a bullish Forex market analyst. Given the following UFO data, which shows "
            f"{strongest_currency} as the strongest currency, provide a detailed bullish analysis. "
            f"Focus on the potential for {strongest_currency} to continue its rally.\n\n"
            f"UFO Data:\n{ufo_data.tail().to_string()}"
        )

        bearish_prompt = (
            f"You are a bearish Forex market analyst. Given the following UFO data, which shows "
            f"{weakest_currency} as the weakest currency, provide a detailed bearish analysis. "
            f"Focus on the potential for {weakest_currency} to continue its decline.\n\n"
            f"UFO Data:\n{ufo_data.tail().to_string()}"
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
