from pydantic import BaseModel, Field
from typing import Optional


class WebSearchInput(BaseModel):
    query: str = Field(
        description="The search query to look up on the web using DuckDuckGo."
    )
    max_results: Optional[int] = Field(
        default=5,
        description="Maximum number of search results to return (default: 5)."
    )
