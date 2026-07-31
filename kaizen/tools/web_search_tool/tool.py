import json
from typing import Optional

from langchain_core.tools import tool

from kaizen.tools.web_search_tool.schemas import WebSearchInput


@tool(args_schema=WebSearchInput)
def web_search_tool(
    query: str,
    max_results: Optional[int] = 5,
) -> str:
    """
    Search the web for information using DuckDuckGo.
    Returns search results as a JSON string containing titles, links, and snippets.
    """
    from kaizen.cli.ui import panels
    from duckduckgo_search import DDGS

    panels.log_tool_start("Searching", f"web: {query}")
    try:
        results = []
        with DDGS() as ddgs:
            ddgs_generator = ddgs.text(query, max_results=max_results)
            for r in ddgs_generator:
                results.append({
                    "title": r.get("title"),
                    "link": r.get("href"),
                    "snippet": r.get("body")
                })

        panels.log_tool_end("Searched", f"web: {query}", success=True, details=f"{len(results)} results")
        return json.dumps(results, indent=2)
    except Exception as e:
        panels.log_tool_end("Searched", f"web: {query}", success=False, details=str(e))
        return json.dumps({"error": f"Failed to search the web: {str(e)}"})
