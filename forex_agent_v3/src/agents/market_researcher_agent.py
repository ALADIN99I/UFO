from .base_agent import Agent

class MarketResearcherAgent(Agent):
    def execute(self, ufo_data):
        """
        Analyzes the UFO data from bullish and bearish perspectives using the LLM.
        """
        strongest_currency = ufo_data.iloc[-1].idxmax()
        weakest_currency = ufo_data.iloc[-1].idxmin()

        bullish_prompt = (
            f"Given that {strongest_currency} is the strongest currency, "
            f"provide a bullish market analysis."
        )

        bearish_prompt = (
            f"Given that {weakest_currency} is the weakest currency, "
            f"provide a bearish market analysis."
        )

        bullish_perspective = self.llm_client.generate_response(bullish_prompt)
        bearish_perspective = self.llm_client.generate_response(bearish_prompt)

        consensus_prompt = (
            f"Synthesize the following bullish and bearish perspectives into a single trading "
            f"recommendation:\n\nBullish: {bullish_perspective}\n\nBearish: {bearish_perspective}"
        )

        consensus = self.llm_client.generate_response(consensus_prompt)

        return {
            "bullish": bullish_perspective,
            "bearish": bearish_perspective,
            "consensus": consensus
        }
