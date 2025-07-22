from .base_agent import Agent

class MarketResearcherAgent(Agent):
    def __init__(self, name, llm_client):
        super().__init__(name)
        self.llm_client = llm_client

    def execute(self, ufo_data):
        """
        Analyzes the UFO data from bullish and bearish perspectives.
        """
        # In a real implementation, the LLM would generate these perspectives.
        # Here, we'll use a simplified logic.
        strongest_currency = ufo_data.iloc[-1].idxmax()
        weakest_currency = ufo_data.iloc[-1].idxmin()

        bullish_perspective = self.llm_client.generate_response(
            f"Provide a bullish analysis based on {strongest_currency} being the strongest currency."
        )

        bearish_perspective = self.llm_client.generate_response(
            f"Provide a bearish analysis based on {weakest_currency} being the weakest currency."
        )

        return {
            "bullish": bullish_perspective,
            "bearish": bearish_perspective,
            "consensus": f"Pairing strongest ({strongest_currency}) against weakest ({weakest_currency})."
        }
