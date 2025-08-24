# Agent Development Plan

Iterative development with minimal increments using Python 3.13.7.

## v0.1: Environment Setup
**What**: Basic project structure + uv config  
**How**: Create pyproject.toml, .gitignore, src/ dir  
**Check**: `uv sync` works, imports resolve

## v0.2: Core Agent Class
**What**: Minimal Agent class skeleton  
**How**: src/agent.py with basic __init__, run() method  
**Check**: Agent() instantiates, run() returns placeholder

## v0.3: LLM Integration
**What**: Connect to local Ollama phi4-mini  
**How**: OpenAIChatCompletionsModel + AsyncOpenAI(base_url="http://localhost:11434/v1")  
**Check**: LLM responds to simple prompt, requires OPENAI_API_KEY env var

## v0.4: Function Tool Decorator
**What**: @function_tool decorator from openai-agents  
**How**: Decorator registers functions as callable tools with automatic schema  
**Check**: Tool registration works, schema generated, agent can access

## v0.5: Tool Execution
**What**: Agent can call registered tools  
**How**: Parse LLM response, execute matching tool  
**Check**: Tool called correctly, output returned

## v0.6: DuckDuckGo Search Tool
**What**: Web search for news articles  
**How**: DDGS().text(topic, max_results=5), format as Title/URL/Description  
**Check**: Returns 5 articles or error message, human-readable format

## v0.7: Multi-Agent System
**What**: ContentPlanner + Writer agents  
**How**: Agent(name, instructions, tools, model) - planner gets articles, writer creates posts  
**Check**: Agents have distinct roles, tools assignment works

## v0.8: Agent Orchestration
**What**: Runner.run_sync coordination  
**How**: content_planner_response → raw_articles → writer_agent → final_output  
**Check**: Full workflow: search articles → plan content → write post

## v0.9: Error Handling
**What**: Robust error management  
**How**: Try/catch, fallbacks, validation  
**Check**: Graceful failure, useful error messages

## v1.0: Tracing & Monitoring
**What**: Execution observability  
**How**: Trace agent runs, performance metrics  
**Check**: Dashboard shows execution flow

## Core Implementation Details

### LLM Configuration (v0.3)
```python
model = OpenAIChatCompletionsModel(
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
```

### Function Tool Example (v0.4-v0.6)
```python
@function_tool
def get_news_articles(topic):
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic}", max_results=5)
    if results:
        return "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
    return f"Could not find news results for {topic}."
```

### Agent Creation (v0.7)
```python
content_planner_agent = Agent(
    name="Content Planner",
    instructions="Plan engaging blog post on {topic}. Gather accurate, up-to-date info and structure content",
    tools=[get_news_articles],
    model=model
)

writer_agent = Agent(
    name="Technical content writer",
    instructions="Create detailed, factually accurate blog post on: {topic}",
    model=model
)
```

### Workflow Orchestration (v0.8)
```python
def openai_agent_workflow(topic):
    # Fetch articles
    content_planner_response = Runner.run_sync(
        content_planner_agent,
        f"Get me articles about {topic}"
    )
    raw_articles = content_planner_response.final_output
    
    # Generate content
    edited_news_response = Runner.run_sync(
        writer_agent,
        raw_articles
    )
    return edited_news_response.final_output
```

## Dependencies by Version
- v0.1: uv
- v0.3: openai
- v0.6: duckduckgo-search
- v0.8: openai-agents (includes Agent, Runner, function_tool)
- v0.9: logging
- v1.0: tracing

## Setup Commands
```bash
# Environment
uv init
uv python pin 3.13.7
uv add openai duckduckgo-search openai-agents
export OPENAI_API_KEY="YOUR_API_KEY"

# Start Ollama
ollama run phi4-mini

# Optional: Jupyter support
uv add nest-asyncio
```

## Requirements
- Tool-calling LLM (phi4-mini supports this)
- OPENAI_API_KEY environment variable
- Ollama running on localhost:11434
