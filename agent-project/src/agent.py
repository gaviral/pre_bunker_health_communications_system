from openai import AsyncOpenAI
import json
import re
from src.tools import execute_tool, get_tool_schemas

class OpenAIChatCompletionsModel:
    def __init__(self, model, openai_client):
        self.model = model
        self.client = openai_client
    
    async def chat(self, messages):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

class Agent:
    def __init__(self, name, instructions, tools=None, model=None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
    
    async def run(self, message):
        # Include tool schemas in prompt
        tools_prompt = "\nAvailable tools: " + json.dumps(get_tool_schemas(), indent=2) if get_tool_schemas() else ""
        prompt = f"{self.instructions}\n\nUser: {message}{tools_prompt}"
        
        response = await self.model.chat([
            {"role": "user", "content": prompt}
        ])
        
        # Simple tool call detection
        tool_pattern = r'call_tool\("([^"]+)",\s*\{([^}]*)\}\)'
        match = re.search(tool_pattern, response)
        
        if match:
            tool_name = match.group(1)
            # Parse args (improved)
            args_str = match.group(2).strip()
            args = {}
            
            if args_str:
                # Parse JSON-like key-value pairs
                import ast
                try:
                    # Try to parse as JSON-like string
                    args_str = args_str.replace("'", '"')  # Convert single quotes to double
                    args_dict = json.loads('{' + args_str + '}')
                    args = {k: str(v) for k, v in args_dict.items()}
                except:
                    # Fallback to simple parsing
                    for arg in args_str.split(','):
                        if ':' in arg:
                            key, value = arg.split(':', 1)
                            args[key.strip().strip('"')] = value.strip().strip('"')
            
            try:
                tool_result = execute_tool(tool_name, args)
                return f"Tool result: {tool_result}"
            except Exception as e:
                return f"Tool error: {str(e)}"
        
        return response

# Setup model
model = OpenAIChatCompletionsModel(
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
