from concurrent.futures import ThreadPoolExecutor
from typing import Annotated, List

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field

from kaizen.tools.subagents.subagents_nodes import subagent_graph


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
    from kaizen.cli.ui import panels
    panels.log_tool_start("Subagents", f"Spawning {len(tasks)} parallel subtasks")
    for idx, t in enumerate(tasks):
        panels.log_action(f"Subtask {idx + 1}", t)

    try:

        def run_worker(task: str):
            from kaizen.cli.ui.panels import thread_local
            thread_local.is_subagent = True
            state = {
                "messages": [
                    HumanMessage(
                        content=f"Please execute the assigned subtask:\n{task}"
                    )
                ],
                "workspace": workspace,
                "snapshot": snapshot,
                "task": task,
                "report": [],
            }
            res = subagent_graph.invoke(state)
            return res.get("report", [])

        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            reports_lists = list(executor.map(run_worker, tasks))

        panels.log_tool_end("Subagents", f"Completed {len(tasks)} parallel subtasks", success=True)
        return "\n\n".join(
            f"### Subagent {idx + 1} Report (Task: {task}):\n{rep[-1].content if rep else ''}"
            for idx, (task, rep) in enumerate(zip(tasks, reports_lists))
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        panels.log_tool_end("Subagents", f"Failed to execute parallel subtasks", success=False)
        return f"Error executing subagents: {str(e)}"
