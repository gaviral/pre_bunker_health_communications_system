# OpenAI Agents SDK with Local LLM

Python framework for production-ready AI agent applications. Streamlined agentic systems with multi-agent collaboration via task delegation and tool usage.

## Core Components

- **Agent Loop**: Iterative task execution with tool usage/result processing
- **Handoff System**: Dynamic task delegation between specialized agents via triaging
- **Guardrails**: Parallel validation pipelines for input sanitization/output safety
- **Tracing**: Built-in observability with execution flow visualization/performance monitoring

LLM: core intelligence powering agent decision-making, NLU, reasoning.

Before technical details: benefits and framework differences.

## Benefits

### Production Readiness

1. Simplified Swarm framework upgrade
2. Built-in rate limiting/error handling
3. Enterprise security for LLM interactions

### Developer Experience

1. Reduced boilerplate vs vanilla implementations
2. Integrated debugging via tracing dashboard
3. Python-native with modern type hints

## Framework Comparison
Many agentic frameworks exist. Quick comparison:
"Pydantic-based validation" definition:

Pydantic validation: ensures input matches expected structure/types/constraints via Pydantic models. Automates type-checking/parsing, raises errors if invalid.

## Workflow

LLM powers workflow decision-making, NLU, reasoning. Stages:

1. **Input Interpretation**: Agent receives input (query/task/external data)
2. **Decision-Making**: LLM decides internal vs external tools. Reasons through prompts, selects approach
3. **Tool Invocation**: Agent decides external tools needed (search/database). Calls tool, processes output
4. **Agent Loop**: LLM iteration enabling:
   - Intermediate output reflection
   - Further action determination
   - Processing until valid response
5. **Task Delegation**: Delegates to specialized sub-agents for complex workflows
6. **Guardrails**: Ensure input/output validation/safety. Prevent unsafe/invalid actions
7. **Response Generation**: LLM synthesizes info into coherent response

Image illustrates complete workflow.

 

### Workflow Summary
- **Input**: User request
- **Agent**: Receives/interprets input
- **Tools**: Calls external tools (search/retrieval)
- **Agent Loop**: Iterates until complete
- **Handoff**: Delegates to specialized agents
- **Guardrails**: Ensures compliance
- **Output**: Delivers final response

Agent SDK example:

## Getting Started
Install Ollama. Obtain OpenAI API key.

### Step 1: Run your LLM model on Ollama

```bash
ollama run phi4-mini  # you can use any model like llama3.2
```
Help: "How to Install Ollama" post or "Generative AI with Local LLM" chapter.

Requires tool-calling LLM (Llama/Qwen/phi4-mini). deepseek-r1 lacks support, causes 400 errors.
Requires OPENAI_API_KEY for requests/tracing:

```bash
export OPENAI_API_KEY="YOUR API KEY GOES HERE"
```
### Step 2: Setup project environment

```bash
uv init agent-project
cd agent-project
uv python pin 3.13.7
```
Modified CrewAI example for Agent SDK.

 

### Step 3: Install dependencies

```bash
uv add openai-agents duckduckgo-search
```
Requires: openai-agents

### Step 4: Create main.py

```python
# main.py
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from duckduckgo_search import DDGS
```

### Step 5: Configure LLM in main.py

```python
# Add to main.py
model = OpenAIChatCompletionsModel( 
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
```
Adjust host/port per config.

### Step 6: Add search function to main.py

DuckDuckGo integration via Function Calling. Fetches 5 articles.

```python
# Add to main.py
@function_tool
def get_news_articles(topic):
    print(f"Running DuckDuckGo search for {topic}...")
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic}", max_results=5)
    if results:
        news_results = "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        print(news_results)
        return news_results
    return f"No results for {topic}."
```
**Explanation:**

- `@function_tool`: Decorator registering `get_news_articles` as tool
- `get_news_articles(topic)`: Takes topic, retrieves articles

**What is happening under the hood:**

- Integrates DuckDuckGo with SDK
- Fetches 5 articles
- Returns readable format or error

### Step 7: Add content planner to main.py

```python
# Add to main.py
content_planner_agent = Agent(
    name="Content Planner",
    instructions="Plan engaging blog post on {topic}. Gather accurate, up-to-date info and structure content",
    tools=[get_news_articles],
    model=model
)
```
**Explanation:**

`content_planner_agent`:
- Plans blog posts
- Fetches news via `get_news_articles`
- Generates outline with model

### Step 8: Add writer agent to main.py

```python
# Add to main.py
writer_agent = Agent(
    name="Technical content writer",
    instructions="Create detailed, factually accurate blog post on: {topic}",
    model=model
)
```
`writer_agent`:
- Produces detailed technical posts
- Uses OpenAI model
- Accepts topic via `{topic}`

### Step 9: Add workflow and main execution

```python
# Add to main.py
def openai_agent_workflow(topic):
    print("Running workflow...")
    # Fetch articles
    content_planner_response = Runner.run_sync(
        content_planner_agent,
        f"Get articles about {topic}"
    )
    raw_articles = content_planner_response.final_output
    
    # Generate content
    edited_news_response = Runner.run_sync(
        writer_agent,
        raw_articles
    )
    edited_article = edited_news_response.final_output
    
    print("Final article:")
    print(edited_article)
    return edited_article

if __name__ == "__main__":
    topic = "Installing Apache Ignite v3 on Docker"
    openai_agent_workflow(topic)
```
`openai_agent_workflow` orchestrates:
- Fetches via `content_planner_agent`
- Refines via `writer_agent`
- Delivers polished article

#### Workflow Functions:
1. **Collection**: `content_planner_agent` gathers DuckDuckGo articles
2. **Refinement**: `writer_agent` crafts detailed post
3. **Output**: Prints/returns final post
 
### Step 10: Run the application

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
uv run main.py
```

Auto-traces runs for tracking/debugging. Access: OpenAI Dashboard.

Enter/click for full image

## Enhancements

Enhancements:

- **Error Handling**: Manage no-article cases
- **Multi-Agent**: Add editor for grammar/tone
- **Parallel**: Use async `Runner.run()` for speed

Example enhancements in separate files:

```python
# editor.py
editor_agent = Agent(
    name="Editor Agent",
    instructions="Proofread blog post for grammar/readability while maintaining meaning",
    handoffs=[content_planner_agent, writer_agent]
)

# async_main.py
import asyncio

async def main():
    result = await Runner.run(editor_agent, topic)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```
 

 

