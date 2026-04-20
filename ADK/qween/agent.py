import ollama
from tools import AVAILABLE_TOOLS

class FinancialAgent:
    def __init__(self, model_name='qwen2.5:0.5b'):
        self.model_name = model_name
        self.system_prompt = (
            "You are a helpful financial assistant with access to tools. "
            "Use tools for EVERY financial query. If a user asks for a price, news, "
            "or chart, you MUST call the appropriate function."
        )

    def run(self, query):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': query}
        ]

        # First pass: Get tool calls
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            tools=list(AVAILABLE_TOOLS.values())
        )

        tool_results = []
        
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                func_name = call.function.name
                args = call.function.arguments
                
                if func_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[func_name](**args)
                    messages.append(response.message)
                    messages.append({'role': 'tool', 'content': str(result)})
                    tool_results.append({"name": func_name, "args": args})

            # Second pass: Get final response
            final_response = ollama.chat(model=self.model_name, messages=messages)
            return final_response.message.content, tool_results
        
        return response.message.content, []