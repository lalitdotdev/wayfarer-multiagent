# tavily_tool.py
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_client: Optional[TavilyClient] = None

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_client() -> TavilyClient:
    """Get or create the Tavily client instance."""
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set in environment variables.")
        _client = TavilyClient(api_key=api_key)
    return _client

def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily. Handles missing keys or API exceptions gracefully.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Formatted search results string
    """
    # Input validation
    if not query or not query.strip():
        logger.warning("Empty search query provided")
        return "Please provide a valid search query."

    try:
        client = get_client()
        logger.info(f"Executing Tavily search for query: '{query}' (max_results: {max_results})")

        # Added timeout parameter if supported by the Tavily client
        response = client.search(
            query=query.strip(),
            max_results=max_results,
            include_answer=True,  # Get AI-generated answer if available
            include_raw_content=False  # We don't need raw content for our use case
        )

        results = []

        # Add the AI answer if available and good
        answer = response.get("answer", "").strip()
        if answer and len(answer) > 20:  # Only include substantial answers
            results.append(f"**Summary:** {answer}")

        # Add individual results
        for i, r in enumerate(response.get("results", []), 1):
            title   = r.get("title", "Untitled").strip()
            url     = r.get("url", "").strip()
            snippet = r.get("content", "").strip()

            # Skip if we don't have essential information
            if not title and not snippet:
                continue

            # Truncate snippet if too long
            if len(snippet) > 300:
                snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

            # Format the result
            result_parts = [f"{i}. **{title}**"]
            if url:
                result_parts.append(f"   {url}")
            if snippet:
                result_parts.append(f"   {snippet}")

            results.append("\n".join(result_parts))

        if not results:
            logger.warning("Tavily search returned no results")
            return "No matching search results found for your query."

        logger.info(f"Tavily search returned {len(results)} results")
        return "\n\n".join(results)

    except ValueError as e:
        # Configuration errors (like missing API key)
        logger.error(f"Tavily configuration error: {e}")
        return "Search service is not properly configured. Please contact support."
    except Exception as e:
        # Handle network errors, rate limits, etc.
        logger.error(f"Error during Tavily search: {type(e).__name__}: {e}")
        # Check if it's a rate limit error
        if "rate limit" in str(e).lower() or "429" in str(e):
            return "Search service is currently experiencing high demand. Please try again in a moment."
        else:
            return "Search service is temporarily unavailable. Please try again later."