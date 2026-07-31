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

    from kaizen.cli.ui import panels

    panels.log_tool_start("Running", command)

    try:
        workspace_path = Path(workspace).resolve()

        import os

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        result = subprocess.run(
            command,
            cwd=workspace_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env=env,
        )

    except subprocess.TimeoutExpired:
        err_msg = (
            "Error: Command execution timed out after 30 seconds.\n"
            "NOTE: Do NOT run persistent background web servers (e.g., uvicorn, flask run, npm start) "
            "via the terminal tool because terminal execution is synchronous.\n"
            "Instead, verify code using syntax checks (`python -m py_compile <file>`), "
            'import tests (`python -c "import app.main"`), or test suites (`pytest`).'
        )
        panels.log_terminal_result(
            command,
            success=False,
            output="Command timed out after 30 seconds",
            exit_code=-1,
        )
        return err_msg

    except Exception as e:
        err_msg = f"Error executing command: {str(e)}"
        panels.log_terminal_result(command, success=False, output=str(e), exit_code=-2)
        return err_msg

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    output_parts = []

    if stdout:
        output_parts.append(stdout)

    if stderr:
        output_parts.append("[Standard Error Output]:\n" + stderr)

    combined_output = "\n\n".join(output_parts)

    if result.returncode != 0:
        panels.log_terminal_result(
            command, success=False, output=combined_output, exit_code=result.returncode
        )
        return (
            combined_output
            or f"Error: Command failed with exit code {result.returncode}."
        )

    panels.log_terminal_result(
        command, success=True, output=combined_output, exit_code=0
    )
    return combined_output or "OK"
