import os
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

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

    print(f"\n[Tool: List Directory] Listing contents of directory '{path}'...")
    try:
        workspace_path = Path(workspace).resolve()

        requested_path = Path(path)

        if requested_path.is_absolute():
            try:
                resolved_dir = requested_path.resolve()

                resolved_dir.relative_to(workspace_path)

            except ValueError:
                return "Error: Access outside workspace is prohibited."

        else:
            resolved_dir = (workspace_path / requested_path).resolve()

            try:
                resolved_dir.relative_to(workspace_path)

            except ValueError:
                return "Error: Access outside workspace is prohibited."

        if not resolved_dir.exists():
            return f"Error: Directory '{path}' does not exist."

        if not resolved_dir.is_dir():
            return f"Error: '{path}' is a file, not a directory. Use read_file to view its content."

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
            return f"Error listing directory '{path}': {str(e)}"

        if not entries:
            return "(empty directory)"

        entries.sort()

        return "\n".join(entries)

    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"
