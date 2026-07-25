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

    print(
        f"\n[Tool: Read File] Reading '{path}' (lines {start_line or 1} to {end_line or 'EOF'})..."
    )
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        if not resolved_path.exists():
            return f"Error: File '{path}' does not exist."

        if not resolved_path.is_file():
            return f"Error: '{path}' is a directory, not a file. Use list_directory to see its contents."

        try:
            content = resolved_path.read_text(encoding="utf-8", errors="replace")

        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"

        lines = content.splitlines()

        MAX_READ_LINES = 1000

        if len(lines) > MAX_READ_LINES and start_line is None and end_line is None:
            return (
                f"Error: File '{path}' is too large ({len(lines)} lines). "
                f"To save tokens, reading files larger than {MAX_READ_LINES} lines requires pagination. "
                f"Please specify 'start_line' and 'end_line' parameters to read specific sections."
            )

        start = start_line or 1
        end = end_line or len(lines)

        if start > end:
            return "Error: start_line must be less than or equal to end_line."

        if start > len(lines):
            return f"Error: Requested start_line ({start}) exceeds the total number of lines in the file ({len(lines)})."

        end = min(end, len(lines))

        output_lines = []
        for i in range(start, end + 1):
            output_lines.append(f"{i}: {lines[i - 1]}")

        return "\n".join(output_lines)

    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"
