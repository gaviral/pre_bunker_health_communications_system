class Agent:
    def __init__(self, name, instructions, tools=None, model=None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
    
    def run(self, message):
        return f"Agent {self.name} processed: {message}"
