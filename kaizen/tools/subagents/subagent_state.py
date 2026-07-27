from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class KaizenWorkerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    workspace: str

    snapshot: str

    task: str

    report: Annotated[list[AnyMessage], add_messages]


class KaizenSubAgentState(TypedDict):
    workspace: str
    snapshot: str
    tasks: list[str]
    reports: Annotated[list[AnyMessage], add_messages]
