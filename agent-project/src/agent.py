from openai import AsyncOpenAI
import json
import re
from src.tools import execute_tool, get_tool_schemas
from src.error_handler import logger, AgentError
from src.tracing import tracer

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
        trace_id = tracer.start_trace(self.name, "run")
        tracer.add_event(trace_id, "input", message)
        
        try:
            logger.info(f"Agent {self.name} processing message: {message[:50]}...")
            
            # Include tool schemas in prompt
            tools_prompt = "\nAvailable tools: " + json.dumps(get_tool_schemas(), indent=2) if get_tool_schemas() else ""
            prompt = f"{self.instructions}\n\nUser: {message}{tools_prompt}"
            
            tracer.add_event(trace_id, "llm_call", {"prompt_length": len(prompt)})
            response = await self.model.chat([
                {"role": "user", "content": prompt}
            ])
            tracer.add_event(trace_id, "llm_response", {"response_length": len(response)})
            
            # Simple tool call detection
            tool_pattern = r'call_tool\("([^"]+)",\s*\{([^}]*)\}\)'
            match = re.search(tool_pattern, response)
            
            if match:
                tool_name = match.group(1)
                logger.info(f"Agent {self.name} calling tool: {tool_name}")
                tracer.add_event(trace_id, "tool_call", {"tool": tool_name})
                
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
                    except Exception as parse_error:
                        logger.warning(f"JSON parsing failed, using fallback: {parse_error}")
                        tracer.add_event(trace_id, "parse_error", str(parse_error))
                        # Fallback to simple parsing
                        for arg in args_str.split(','):
                            if ':' in arg:
                                key, value = arg.split(':', 1)
                                args[key.strip().strip('"')] = value.strip().strip('"')
                
                try:
                    tool_result = execute_tool(tool_name, args)
                    logger.info(f"Tool {tool_name} executed successfully")
                    tracer.add_event(trace_id, "tool_success", {"tool": tool_name, "result_length": len(str(tool_result))})
                    result = f"Tool result: {tool_result}"
                    tracer.end_trace(trace_id, result)
                    return result
                except Exception as e:
                    logger.error(f"Tool {tool_name} execution failed: {str(e)}")
                    tracer.add_event(trace_id, "tool_error", {"tool": tool_name, "error": str(e)})
                    result = f"Tool error: {str(e)}"
                    tracer.end_trace(trace_id, result)
                    return result
            
            logger.info(f"Agent {self.name} completed without tool calls")
            tracer.end_trace(trace_id, response)
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} error: {str(e)}")
            tracer.add_event(trace_id, "agent_error", str(e))
            result = f"Agent error: {str(e)}"
            tracer.end_trace(trace_id, result)
            return result

# Setup model
model = OpenAIChatCompletionsModel(
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
