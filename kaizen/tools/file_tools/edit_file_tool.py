from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from kaizen.tools.file_tools.base import path_resolver
from kaizen.tools.file_tools.schemas import EditFileInput


@tool(args_schema=EditFileInput)
def edit_file(
    path: str,
    old_text: str,
    new_text: str,
    workspace: Annotated[str, InjectedState("workspace")],
    replace_all: bool = False,
) -> str:
    """
    Replace a block of text ('old_text') with new text ('new_text') inside a file.
    The old_text must match the current file contents exactly.
    """

    from kaizen.cli.ui import panels
    panels.log_tool_start("Editing", path)
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        if not resolved_path.exists():
            err_msg = f"Error: File '{path}' does not exist."
            panels.log_tool_end("Edited", path, success=False, details="not found")
            return err_msg

        if not resolved_path.is_file():
            err_msg = f"Error: '{path}' is not a file."
            panels.log_tool_end("Edited", path, success=False, details="not file")
            return err_msg

        try:
            content = resolved_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            err_msg = f"Error reading file '{path}': {str(e)}"
            panels.log_tool_end("Edited", path, success=False, details="read error")
            return err_msg

        matches_count = content.count(old_text)

        if matches_count == 0:
            err_msg = (
                "Error: The specified old_text was not found in the file. "
                "Ensure that white spaces, line endings, and indentation match exactly."
            )
            panels.log_tool_end("Edited", path, success=False, details="block not found")
            return err_msg

        if matches_count > 1 and not replace_all:
            err_msg = (
                f"Error: The old_text matches {matches_count} occurrences in the file. "
                "To prevent corrupting other parts of the code, please include more surrounding context "
                "(additional lines before or after) to make the block unique, or set replace_all=True."
            )
            panels.log_tool_end("Edited", path, success=False, details="multiple matches")
            return err_msg

        if replace_all:
            updated_content = content.replace(old_text, new_text)
        else:
            updated_content = content.replace(old_text, new_text, 1)

        try:
            resolved_path.write_text(updated_content, encoding="utf-8")
        except Exception as e:
            err_msg = f"Error writing updates to file '{path}': {str(e)}"
            panels.log_tool_end("Edited", path, success=False, details="write error")
            return err_msg

        panels.log_tool_end("Edited", path, success=True)
        return "OK"

    except Exception as e:
        err_msg = f"Error: An unexpected error occurred: {str(e)}"
        panels.log_tool_end("Edited", path, success=False, details="error")
        return err_msg
