from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class KaizenState(TypedDict):
    # Message history containing user inputs, agent outputs, and tool outputs
    messages: Annotated[list[AnyMessage], add_messages]

    # Workspace path
    workspace: str

    # Project structure snapshot
    snapshot: str
    todos: list[dict]
