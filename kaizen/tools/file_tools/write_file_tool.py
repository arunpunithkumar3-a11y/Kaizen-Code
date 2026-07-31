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

    from kaizen.cli.ui import panels
    panels.log_tool_start("Writing", path)
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            resolved_path.write_text(content, encoding="utf-8")
        except Exception as e:
            err_msg = f"Error writing file '{path}': {str(e)}"
            panels.log_tool_end("Wrote", path, success=False, details="write error")
            return err_msg

        lines_count = len(content.splitlines())
        panels.log_tool_end("Wrote", path, success=True, details=f"{lines_count} lines")
        return "OK"

    except PermissionError as e:
        err_msg = f"Error: {str(e)}"
        panels.log_tool_end("Wrote", path, success=False, details="permission error")
        return err_msg
    except Exception as e:
        err_msg = f"Error: An unexpected error occurred: {str(e)}"
        panels.log_tool_end("Wrote", path, success=False, details="error")
        return err_msg
