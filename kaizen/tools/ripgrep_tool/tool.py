import json
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.ripgrep_tool.schemas import RipgrepInput


@tool(args_schema=RipgrepInput)
def ripgrep(
    pattern: str,
    workspace: Annotated[str, InjectedState("workspace")],
):
    """
    Search the codebase for a text pattern or regex query.
    Returns a list of dicts with file path, line number, and matching text.
    On error, returns a dict with 'error' key.
    """

    from rich.console import Console
    Console().print(f"\n[bold #ffaf5f]Search:[/bold #ffaf5f] [white]{pattern}[/white]")
    try:
        workspace_path = Path(workspace).resolve()

        if not shutil.which("rg"):
            return {
                "error": "ripgrep ('rg') executable is not installed or not in PATH."
            }

        result = subprocess.run(
            [
                "rg",
                "--json",
                "-n",
                "--smart-case",
                "--hidden",
                "--glob",
                "!.git",
                "--glob",
                "!node_modules",
                "--glob",
                "!dist",
                "--glob",
                "!build",
                "--glob",
                "!coverage",
                "--glob",
                "!venv",
                "--glob",
                "!.venv",
                "--glob",
                "!__pycache__",
                "--glob",
                "!egg-info",
                "--glob",
                "!kaizen.egg-info",
                "--max-count",
                "30",
                pattern,
                str(workspace_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        if result.returncode == 1:
            return []

        if result.returncode != 0:
            return {"error": f"Error executing ripgrep: {result.stderr.strip()}"}

        matches = []
        MAX_TOTAL_MATCHES = 50

        for idx, line in enumerate(result.stdout.splitlines()):
            if idx >= MAX_TOTAL_MATCHES:
                matches.append(
                    {
                        "file": None,
                        "line": None,
                        "text": f"... (further matches truncated. Total capped at {MAX_TOTAL_MATCHES})",
                    }
                )
                break

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") != "match":
                continue

            data = event.get("data", {})
            path = data.get("path", {}).get("text")
            line_number = data.get("line_number")
            text = data.get("lines", {}).get("text", "").strip()

            if not path or not line_number:
                continue

            try:
                file_rel = str(
                    Path(path).resolve().relative_to(workspace_path)
                ).replace("\\", "/")
            except Exception:
                file_rel = path

            if len(text) > 120:
                text = text[:120] + "..."

            matches.append({"file": file_rel, "line": line_number, "text": text})

        return json.dumps(matches)

    except subprocess.TimeoutExpired:
        return {"error": "ripgrep command timed out."}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
