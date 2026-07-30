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

    from kaizen.cli.ui import panels
    panels.log_tool_start("Searching", pattern)
    try:
        workspace_path = Path(workspace).resolve()

        if not shutil.which("rg"):
            err_res = {
                "error": "ripgrep ('rg') executable is not installed or not in PATH."
            }
            panels.log_tool_end("Searched", pattern, success=False, details="no rg bin")
            return err_res

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
            panels.log_tool_end("Searched", pattern, success=True, details="0 matches")
            return []

        if result.returncode != 0:
            err_res = {"error": f"Error executing ripgrep: {result.stderr.strip()}"}
            panels.log_tool_end("Searched", pattern, success=False, details="rg error")
            return err_res

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

        panels.log_tool_end("Searched", pattern, success=True, details=f"{len(matches)} matches")
        return json.dumps(matches)

    except subprocess.TimeoutExpired:
        err_res = {"error": "ripgrep command timed out."}
        panels.log_tool_end("Searched", pattern, success=False, details="timeout")
        return err_res

    except Exception as e:
        err_res = {"error": f"Unexpected error: {str(e)}"}
        panels.log_tool_end("Searched", pattern, success=False, details="error")
        return err_res
