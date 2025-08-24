from src.agent import Agent
from src.search_tool import get_news_articles
from src.agent import model

content_planner_agent = Agent(
    name="Content Planner",
    instructions="Plan engaging blog post on given topic. Use get_news_articles tool to gather current info. Format response as: call_tool(\"get_news_articles\", {\"topic\": \"topic_here\"})",
    tools=[get_news_articles],
    model=model
)

writer_agent = Agent(
    name="Technical Writer",
    instructions="Create detailed, accurate blog post from provided research. Structure with intro, main content, conclusion.",
    model=model
)
