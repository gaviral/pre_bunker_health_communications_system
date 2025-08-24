import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentError(Exception):
    pass

class ToolError(Exception):
    pass

def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise AgentError(f"Execution failed: {str(e)}")
