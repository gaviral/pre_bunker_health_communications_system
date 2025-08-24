from src.tools import function_tool
from duckduckgo_search import DDGS

@function_tool
def get_news_articles(topic: str) -> str:
    """Search for news articles on given topic"""
    try:
        ddg_api = DDGS()
        results = ddg_api.text(topic, max_results=5)
        
        if results:
            formatted = []
            for result in results:
                formatted.append(
                    f"Title: {result['title']}\n"
                    f"URL: {result['href']}\n"
                    f"Description: {result['body']}"
                )
            return "\n\n".join(formatted)
        return f"No articles found for: {topic}"
    except Exception as e:
        return f"Search error: {str(e)}"
