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
    from rich.console import Console
    console = Console()
    console.print(f"\n[bold #875fdf]Subagents:[/bold #875fdf] Spawning {len(tasks)} subagents in parallel...")
    for idx, t in enumerate(tasks):
        console.print(f"  [bold #875fdf]•[/bold #875fdf] Task {idx + 1}: [white]{t}[/white]")

    try:

        def run_worker(task: str):
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

        return "\n\n".join(
            f"### Subagent {idx + 1} Report (Task: {task}):\n{rep[-1].content if rep else ''}"
            for idx, (task, rep) in enumerate(zip(tasks, reports_lists))
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"Error executing subagents: {str(e)}"
