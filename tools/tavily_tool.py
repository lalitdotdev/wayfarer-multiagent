# tavily_tool.py
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set in environment variables.")
        _client = TavilyClient(api_key=api_key)
    return _client

def tavily_search(query: str) -> str:
    """
    Search the web using Tavily. Handles missing keys or API exceptions gracefully.
    """
    try:
        client = get_client()
        response = client.search(
            query=query,
            max_results=5
        )
        results = []
        for i, r in enumerate(response.get("results", []), 1):
            title   = r.get("title", "Unknown")
            url     = r.get("url", "")
            snippet = r.get("content", "").strip()
            if len(snippet) > 300:
                snippet = snippet[:300].rsplit(" ", 1)[0] + "..."
            results.append(f"{i}. **{title}**\n   {url}\n   {snippet}")
        
        if not results:
            return "No matching search results found."
            
        return "\n\n".join(results)
    except Exception as e:
        return f"Search service unavailable: {str(e)}"