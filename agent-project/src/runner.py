import asyncio

class Runner:
    @staticmethod
    def run_sync(agent, message):
        """Synchronous wrapper for async agent execution"""
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, use create_task
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(agent.run(message))
            else:
                result = loop.run_until_complete(agent.run(message))
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(agent.run(message))
            finally:
                loop.close()
        
        return type('Result', (), {'final_output': result})()
    
    @staticmethod
    async def run(agent, message):
        """Async agent execution"""
        result = await agent.run(message)
        return type('Result', (), {'final_output': result})()

# Workflow function
async def openai_agent_workflow(topic):
    from src.agents import content_planner_agent, writer_agent
    
    # Step 1: Get articles (use async version in async context)
    planner_response = await Runner.run(
        content_planner_agent,
        f"Research and gather articles about: {topic}"
    )
    raw_articles = planner_response.final_output
    
    # Step 2: Write post
    writer_response = await Runner.run(
        writer_agent,
        f"Create blog post from this research: {raw_articles}"
    )
    
    return writer_response.final_output
