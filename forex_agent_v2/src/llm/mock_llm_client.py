class MockLLMClient:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_response(self, prompt):
        """
        Simulates generating a response from the LLM.
        """
        if "bullish" in prompt:
            return "Bullish analysis: The strongest currency is showing strong upward momentum."
        elif "bearish" in prompt:
            return "Bearish analysis: The weakest currency is showing strong downward momentum."
        elif "optimal trade" in prompt:
            return "Trade decision: Buy the strongest currency and sell the weakest currency."
        elif "risk" in prompt:
            return "Risk assessment: The trade has a moderate level of risk."
        elif "authorized" in prompt:
            return "Authorization: The trade is authorized."
        else:
            return "No specific response for this prompt."
