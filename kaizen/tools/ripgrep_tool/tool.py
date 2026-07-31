import json
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
        import os

        import python_ripgrep

        globs_list = [
            "!.git",
            "!node_modules",
            "!dist",
            "!build",
            "!coverage",
            "!venv",
            "!.venv",
            "!__pycache__",
            "!egg-info",
            "!kaizen.egg-info",
        ]

        results = python_ripgrep.search(
            patterns=[pattern],
            paths=[os.path.abspath(workspace)],
            globs=globs_list,
            line_number=True,
            heading=True,
        )

        main_data = []
        total_matches = 0
        MAX_TOTAL_MATCHES = 50
        truncated = False

        for line in results:
            if not line.strip():
                continue
            if total_matches >= MAX_TOTAL_MATCHES:
                truncated = True
                break

            data = line.splitlines()
            if not data:
                continue
            path = data[0]
            metadata = []

            for d in data[1:]:
                if total_matches >= MAX_TOTAL_MATCHES:
                    truncated = True
                    break

                m = d.split(":", 1)
                line_number = m[0]
                text = m[1]

                metadata.append({"line_number": line_number, "text": text})
                total_matches += 1

            main_data.append({"file": str(Path(path).resolve()), "metadata": metadata})

        if truncated:
            main_data.append(
                {
                    "file": None,
                    "metadata": [
                        {
                            "line_number": None,
                            "text": f"... (further matches truncated. Total capped at {MAX_TOTAL_MATCHES})",
                        }
                    ],
                }
            )

        panels.log_tool_end(
            "Searched", pattern, success=True, details=f"{total_matches} matches"
        )
        return json.dumps(main_data)

    except Exception as e:
        panels.log_tool_end("Searched", pattern, success=False, details="error")
        return {"error": str(e)}
