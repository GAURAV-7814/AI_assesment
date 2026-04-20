import google.generativeai as genai
from tools import FINANCIAL_TOOLS

class FinancialAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-3-flash-preview',
            tools=FINANCIAL_TOOLS,
            system_instruction=(
                "You are a professional financial AI agent. Use the provided tools "
                "to answer queries. For Indian stocks, append .NS for NSE. "
                "Summarize data professionally and clearly."
            )
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def ask(self, query: str):
        """Sends a message to the agent and returns the response."""
        response = self.chat.send_message(query)
        return response