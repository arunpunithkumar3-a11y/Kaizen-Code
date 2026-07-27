from typing import Annotated, List

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field

from kaizen.tools.subagents.subagents_nodes import subagents_graph


class SubAgentToolInput(BaseModel):
    """The list of subtasks that should be executed by parallel subagents."""

    tasks: List[str] = Field(
        description="A list of independent, non-overlapping tasks or subtasks to execute in parallel using subagents."
    )


@tool(args_schema=SubAgentToolInput)
def subagent_tool(
    tasks: List[str],
    workspace: Annotated[str, InjectedState("workspace")],
    snapshot: Annotated[str, InjectedState("snapshot")],
) -> str:
    """
    Run multiple subagents in parallel to execute a list of independent subtasks.
    Each subagent operates on the codebase independently and returns its final task report.
    The tool returns the consolidated reports from all spawned subagents.
    """
    print(f"\n[Tool: SubAgent] Spawning {len(tasks)} subagents in parallel...")
    for idx, t in enumerate(tasks):
        print(f"  - Task {idx + 1}: {t}")

    try:
        # Invoke the coordinator graph synchronously
        result = subagents_graph.invoke(
            {
                "workspace": workspace,
                "snapshot": snapshot,
                "tasks": tasks,
                "reports": [],
            }
        )

        reports = result.get("reports", [])
        formatted_reports = []
        for idx, report_msg in enumerate(reports):
            # Extract content from report message
            content = getattr(report_msg, "content", str(report_msg))
            # Find which task this report belongs to
            task_desc = tasks[idx] if idx < len(tasks) else "Unknown Task"
            formatted_reports.append(
                f"### Subagent {idx + 1} Report (Task: {task_desc}):\n{content}"
            )

        return "\n\n".join(formatted_reports)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error executing subagents: {str(e)}"
