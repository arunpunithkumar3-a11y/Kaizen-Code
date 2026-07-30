from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from kaizen.core.engine.nodes import (
    agent,
    approval_node,
    route_after_approval,
    scanner,
    tool_node,
)
from kaizen.core.engine.state import KaizenState
from kaizen.storage.db.sqlite import get_sqlite_checkpointer

workflow = StateGraph(KaizenState)

workflow.add_node("scanner", scanner)
workflow.add_node("agent", agent)
workflow.add_node("tool_node", tool_node)
workflow.add_node("approval", approval_node)

workflow.add_edge(START, "scanner")
workflow.add_edge("scanner", "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "approval",
        "__end__": END,
    },
)
workflow.add_conditional_edges(
    "approval", route_after_approval, {"agent": "agent", "tools": "tool_node"}
)
workflow.add_edge("tool_node", "agent")

checkpointer = get_sqlite_checkpointer()
builder = workflow.compile(checkpointer=checkpointer)
