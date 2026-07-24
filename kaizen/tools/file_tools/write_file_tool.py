from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.file_tools.schemas import WriteFileInput


@tool(args_schema=WriteFileInput)
def write_file(
    path: str,
    content: str,
    workspace: Annotated[str, InjectedState("workspace")],
) -> str:
    """
    Create a new file or completely overwrite an existing file.
    Only relative file paths inside the workspace are allowed.
    """

    print(f"\n[Tool: Write File] Writing '{path}' ({len(content)} chars)...")
    try:
        workspace_path = Path(workspace).resolve()

        requested_path = Path(path)

        if requested_path.is_absolute():
            try:
                resolved_path = requested_path.resolve()

                resolved_path.relative_to(workspace_path)

            except ValueError:
                return "Error: Access outside workspace is prohibited."

        else:
            resolved_path = (workspace_path / requested_path).resolve()

            try:
                resolved_path.relative_to(workspace_path)

            except ValueError:
                return "Error: Access outside workspace is prohibited."

        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            resolved_path.write_text(content, encoding="utf-8")

        except Exception as e:
            return f"Error writing file '{path}': {str(e)}"

        return "OK"

    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"
