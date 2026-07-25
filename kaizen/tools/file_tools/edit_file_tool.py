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

    print(
        f"\n[Tool: Edit File] Modifying '{path}' (replacing a block of {len(old_text)} chars)..."
    )
    try:
        resolved_path = path_resolver(workspace=workspace, path=path)
        if not resolved_path.exists():
            return f"Error: File '{path}' does not exist."

        if not resolved_path.is_file():
            return f"Error: '{path}' is not a file."

        try:
            content = resolved_path.read_text(encoding="utf-8", errors="replace")

        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"

        matches_count = content.count(old_text)

        if matches_count == 0:
            return (
                "Error: The specified old_text was not found in the file. "
                "Ensure that white spaces, line endings, and indentation match exactly."
            )

        if matches_count > 1 and not replace_all:
            return (
                f"Error: The old_text matches {matches_count} occurrences in the file. "
                "To prevent corrupting other parts of the code, please include more surrounding context "
                "(additional lines before or after) to make the block unique, or set replace_all=True."
            )

        if replace_all:
            updated_content = content.replace(old_text, new_text)

        else:
            updated_content = content.replace(old_text, new_text, 1)

        try:
            resolved_path.write_text(updated_content, encoding="utf-8")

        except Exception as e:
            return f"Error writing updates to file '{path}': {str(e)}"

        return "OK"

    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"
