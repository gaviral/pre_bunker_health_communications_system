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
### Step 2: Activate your conda environment

```bash
conda activate YOUR_ENV
jupyter notebook # assume that, you already have the jupyter installed on conda
```
Modified CrewAI example for Agent SDK. Full notebook available.

 

### Step 3: Install necessary packages

New notebook, install:

```bash
!pip install -U openai-agents duckduckgo-search
```
Requires: openai-agents

### Step 4: Import libraries

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from duckduckgo_search import DDGS
```
#### Optional

```bash
!pip install nest-asyncio
```
```python
import nest_asyncio
nest_asyncio.apply()
```
Jupyter/Colab: prevents "RuntimeError: event loop running"

### Step 5: Configure the LLM

```python
model = OpenAIChatCompletionsModel( 
    model="phi4-mini",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1")
)
```
Adjust host/port per config.

### Step 6: Using Function Calling

DuckDuckGo integration via Function Calling. Fetches 5 articles.

```python
@function_tool
def get_news_articles(topic):
    print(f"Running DuckDuckGo news search for {topic}...")
    
    # DuckDuckGo search
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} ", max_results=5)
    if results:
        news_results = "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        print(news_results)
        return news_results
    else:
        return f"Could not find news results for {topic}."
```
**Explanation:**

- `@function_tool`: Decorator registering `get_news_articles` as tool
- `get_news_articles(topic)`: Takes topic, retrieves articles

**What is happening under the hood:**

- Integrates DuckDuckGo with SDK
- Fetches 5 articles
- Returns readable format or error

### Step 7: Create the content_planner_agent

Agent: name/instructions/tools for articles.

```python
content_planner_agent = Agent(
    name="Content Planner",
    instructions="You are tasked with planning an engaging and informative blog post on {topic}. Your goal is to gather accurate, up-to-date information and structure the content",
    tools=[get_news_articles],
    model=model
)
```
**Explanation:**

`content_planner_agent`:
- Plans blog posts
- Fetches news via `get_news_articles`
- Generates outline with model

### Step 8: Create the writer_agent

```python
writer_agent = Agent(
    name="Technical content writer",
    instructions="You are the technical content writer assigned to create a detailed and factually accurate blog post on: {topic}",
    model=model
)
```
`writer_agent`:
- Produces detailed technical posts
- Uses OpenAI model
- Accepts topic via `{topic}`

### Step 9: Agent workflow

```python
# Agent workflow
def openai_agent_workflow(topic):
    print("Running Agent workflow...")
    # Step 1: Search and fetch articles by the content_planner_agent agent
    content_planner_response = Runner.run_sync(
        content_planner_agent,
        f"Get me the articles about {topic} "
    )
    
    # Access the content from Run Result object
    raw_articles = content_planner_response.final_output
    
    # Step 2: Pass articles to editor for final review
    edited_news_response = Runner.run_sync(
        writer_agent,
        raw_articles
    )
    
    # Access the content from RunResult object
    edited_article = edited_news_response.final_output
    
    print("Final article:")
    print(edited_article)
    
    return edited_article
topic = "Step by step example of installing Apache Ignite v3 on Docker."
print(openai_agent_workflow(topic))
```
`openai_agent_workflow` orchestrates:
- Fetches via `content_planner_agent`
- Refines via `writer_agent`
- Delivers polished article

#### Workflow Functions:
1. **Collection**: `content_planner_agent` gathers DuckDuckGo articles
2. **Refinement**: `writer_agent` crafts detailed post
3. **Output**: Prints/returns final post
 
### Step 10: Tracing

Auto-traces runs for tracking/debugging. Access: OpenAI Dashboard.

Enter/click for full image

## Enhancements

Enhancements:

- **Error Handling**: Manage no-article cases
- **Multi-Agent**: Add editor for grammar/tone
- **Parallel**: Use async `Runner.run()` for speed

Example async orchestration:

```python
# An editor agent for grammar and tone improvements.
editor_agent = Agent(
    name="Editor Agent",
    instructions="Proofread the given blog post for grammatical errors and alignment with human language for better readability while maintaining its original meaning.",
    handoffs=[content_planner_agent, writer_agent]
)
```
```python
# Agent orchestration
async def main():
    result = await Runner.run(editor_agent, topic)
    print(result.final_output)
```
 

 

