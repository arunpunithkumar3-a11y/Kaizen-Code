from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class KaizenState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    workspace: str
    summary: str
    snapshot: str
    todos: list[dict]
