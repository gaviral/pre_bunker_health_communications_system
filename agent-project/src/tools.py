import inspect
import json
from typing import Dict, Any, Callable

registered_tools = {}

def function_tool(func: Callable) -> Callable:
    """Decorator to register function as tool"""
    sig = inspect.signature(func)
    schema = {
        "name": func.__name__,
        "description": func.__doc__ or f"Tool: {func.__name__}",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": list(sig.parameters.keys())
        }
    }
    
    for param_name, param in sig.parameters.items():
        schema["parameters"]["properties"][param_name] = {
            "type": "string",  # Simplified for now
            "description": f"Parameter {param_name}"
        }
    
    registered_tools[func.__name__] = {
        "function": func,
        "schema": schema
    }
    return func

def get_tool_schemas():
    return [tool["schema"] for tool in registered_tools.values()]

def execute_tool(name: str, args: Dict[str, Any]):
    if name in registered_tools:
        return registered_tools[name]["function"](**args)
    raise ValueError(f"Tool {name} not found")
