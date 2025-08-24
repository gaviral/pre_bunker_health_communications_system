from openai import AsyncOpenAI

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
    
    def run(self, message):
        return f"Agent {self.name} processed: {message}"

# Setup model
model = OpenAIChatCompletionsModel(
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
