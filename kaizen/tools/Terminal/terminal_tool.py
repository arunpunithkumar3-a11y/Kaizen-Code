import subprocess
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.Terminal.schemas import TerminalInput


@tool(args_schema=TerminalInput)
def terminal(
    command: str,
    workspace: Annotated[str, InjectedState("workspace")],
) -> str:
    """
    Execute a terminal command inside the workspace.
    DO NOT execute long-running background servers (e.g. uvicorn, flask run, npm start) as terminal execution is synchronous.
    """

    from rich.console import Console
    Console().print(f"\n[bold #8a8a8a]System command:[/bold #8a8a8a] [white]{command}[/white]")

    try:
        workspace_path = Path(workspace).resolve()

        result = subprocess.run(
            command,
            cwd=workspace_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

    except subprocess.TimeoutExpired:
        return (
            "Error: Command execution timed out after 30 seconds.\n"
            "NOTE: Do NOT run persistent background web servers (e.g., uvicorn, flask run, npm start) "
            "via the terminal tool because terminal execution is synchronous.\n"
            "Instead, verify code using syntax checks (`python -m py_compile <file>`), "
            'import tests (`python -c "import app.main"`), or test suites (`pytest`).'
        )

    except Exception as e:
        return f"Error executing command: {str(e)}"

    stdout = result.stdout.strip()

    stderr = result.stderr.strip()

    output_parts = []

    if stdout:
        output_parts.append(stdout)

    if stderr:
        output_parts.append("[Standard Error Output]:\n" + stderr)

    combined_output = "\n\n".join(output_parts)

    if result.returncode != 0:
        return (
            combined_output
            or f"Error: Command failed with exit code {result.returncode}."
        )

    return combined_output or "OK"
