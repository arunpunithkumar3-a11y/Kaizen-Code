from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.file_tools.base import path_resolver
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

    from rich.console import Console
    Console().print(f"\n[bold #00ff87]File write:[/bold #00ff87] [white]{path}[/white]")
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            resolved_path.write_text(content, encoding="utf-8")

        except Exception as e:
            return f"Error writing file '{path}': {str(e)}"

        return "OK"

    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"
