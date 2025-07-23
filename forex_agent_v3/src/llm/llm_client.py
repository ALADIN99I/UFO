from openai import OpenAI

class LLMClient:
    def __init__(self, api_key, model="deepseek/deepseek-chat-v3-0324:free"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    def generate_response(self, prompt):
        """
        Generates a response from the LLM.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenRouter LLM: {e}")
            # Implement more robust error handling and retry mechanisms here
            return "Error: Could not get response from LLM."
