import os
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.file_tools.base import path_resolver
from kaizen.tools.file_tools.schemas import ListDirectoryInput


@tool(args_schema=ListDirectoryInput)
def list_directory(
    workspace: Annotated[str, InjectedState("workspace")],
    path: str = ".",
) -> str:
    """
    List contents of a directory and all its subdirectories recursively in the workspace.
    Filters out ignored folders (.git, node_modules, etc.) to optimize tokens.
    """

    from kaizen.cli.ui import panels
    panels.log_tool_start("Listing", path)
    try:
        workspace_path = Path(workspace).resolve()
        resolved_dir = path_resolver(workspace=workspace, path=path)

        if not resolved_dir.exists():
            err_msg = f"Error: Directory '{path}' does not exist."
            panels.log_tool_end("Listed", path, success=False, details="not found")
            return err_msg

        if not resolved_dir.is_dir():
            err_msg = f"Error: '{path}' is a file, not a directory. Use read_file to view its content."
            panels.log_tool_end("Listed", path, success=False, details="is file")
            return err_msg

        IGNORE_NAMES = {
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            "dist",
            "build",
            ".next",
            ".pytest_cache",
            ".mypy_cache",
            ".idea",
            ".vscode",
            "coverage",
            ".tox",
            "target",
            "vendor",
            ".cache",
            "egg-info",
            "kaizen.egg-info",
        }

        entries = []

        try:
            for root, dirs, files in os.walk(resolved_dir):
                dirs[:] = [
                    d for d in dirs if d not in IGNORE_NAMES and not d.startswith(".")
                ]

                for d in dirs:
                    dir_abs_path = Path(root) / d
                    dir_rel_path = dir_abs_path.relative_to(workspace_path)
                    entries.append(f"[DIR]  {dir_rel_path.as_posix()}/")

                for file in files:
                    if file.startswith(".") and file not in {".env", ".gitignore"}:
                        continue

                    file_abs_path = Path(root) / file
                    file_rel_path = file_abs_path.relative_to(workspace_path)
                    size_kb = file_abs_path.stat().st_size / 1024.0
                    entries.append(
                        f"[FILE] {file_rel_path.as_posix()} ({size_kb:.1f} KB)"
                    )

        except Exception as e:
            err_msg = f"Error listing directory '{path}': {str(e)}"
            panels.log_tool_end("Listed", path, success=False, details="read error")
            return err_msg

        if not entries:
            panels.log_tool_end("Listed", path, success=True, details="empty")
            return "(empty directory)"

        entries.sort()
        panels.log_tool_end("Listed", path, success=True, details=f"{len(entries)} items")
        return "\n".join(entries)

    except PermissionError as e:
        err_msg = f"Error: {str(e)}"
        panels.log_tool_end("Listed", path, success=False, details="permission error")
        return err_msg
    except Exception as e:
        err_msg = f"Error: An unexpected error occurred: {str(e)}"
        panels.log_tool_end("Listed", path, success=False, details="error")
        return err_msg
