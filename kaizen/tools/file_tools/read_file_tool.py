from typing import Annotated, Optional

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.file_tools.base import path_resolver
from kaizen.tools.file_tools.schemas import ReadFileInput


@tool(args_schema=ReadFileInput)
def read_file(
    workspace: Annotated[str, InjectedState("workspace")],
    path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
) -> str:
    """
    Read a file's content or a specific line range.
    Only relative file paths inside the workspace are allowed.
    """

    from kaizen.cli.ui import panels
    panels.log_tool_start("Reading", path)
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        if not resolved_path.exists():
            err_msg = f"Error: File '{path}' does not exist."
            panels.log_tool_end("Read", path, success=False, details="not found")
            return err_msg

        if not resolved_path.is_file():
            err_msg = f"Error: '{path}' is a directory, not a file. Use list_directory to see its contents."
            panels.log_tool_end("Read", path, success=False, details="directory")
            return err_msg

        try:
            content = resolved_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            err_msg = f"Error reading file '{path}': {str(e)}"
            panels.log_tool_end("Read", path, success=False, details="read error")
            return err_msg

        lines = content.splitlines()

        MAX_READ_LINES = 1000

        if len(lines) > MAX_READ_LINES and start_line is None and end_line is None:
            err_msg = (
                f"Error: File '{path}' is too large ({len(lines)} lines). "
                f"To save tokens, reading files larger than {MAX_READ_LINES} lines requires pagination. "
                f"Please specify 'start_line' and 'end_line' parameters to read specific sections."
            )
            panels.log_tool_end("Read", path, success=False, details="too large")
            return err_msg

        start = start_line or 1
        end = end_line or len(lines)

        if start > end:
            err_msg = "Error: start_line must be less than or equal to end_line."
            panels.log_tool_end("Read", path, success=False, details="invalid range")
            return err_msg

        if start > len(lines):
            err_msg = f"Error: Requested start_line ({start}) exceeds the total number of lines in the file ({len(lines)})."
            panels.log_tool_end("Read", path, success=False, details="out of bounds")
            return err_msg

        end = min(end, len(lines))

        output_lines = []
        for i in range(start, end + 1):
            output_lines.append(f"{i}: {lines[i - 1]}")

        count = end - start + 1
        panels.log_tool_end("Read", path, success=True, details=f"lines {start}-{end}, {count} lines")
        return "\n".join(output_lines)

    except PermissionError as e:
        err_msg = f"Error: {str(e)}"
        panels.log_tool_end("Read", path, success=False, details="permission error")
        return err_msg
    except Exception as e:
        err_msg = f"Error: An unexpected error occurred: {str(e)}"
        panels.log_tool_end("Read", path, success=False, details="error")
        return err_msg
