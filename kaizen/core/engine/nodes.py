import os

from langgraph.prebuilt import ToolNode

from kaizen.core.engine.state import KaizenState
from kaizen.core.modules.agents.coder import CoderService
from kaizen.core.modules.agents.scanner import ScannerService
from kaizen.tools.file_tools.edit_file_tool import edit_file
from kaizen.tools.file_tools.list_dir_tool import list_directory
from kaizen.tools.file_tools.read_file_tool import read_file
from kaizen.tools.file_tools.write_file_tool import write_file
from kaizen.tools.ripgrep_tool.tool import ripgrep
from kaizen.tools.Terminal.terminal_tool import terminal
from kaizen.tools.todo.todo import write_todos

# Developer Agent tools
developer_tools = [
    read_file,
    write_file,
    edit_file,
    list_directory,
    ripgrep,
    terminal,
    write_todos,
]

# Built-in LangGraph ToolNode instance, mapped to state's messages key
tool_node = ToolNode(developer_tools, messages_key="messages")

coder_service = CoderService()
scanner_service = ScannerService()


def scanner(state: KaizenState) -> dict:
    """
    Scanner node. Scans the workspace directory and saves a snapshot to the state.
    """
    if state.get("snapshot"):
        return {}
    print("\n🔍 [Kaizen Scanner] Scanning project...")
    workspace = state.get("workspace", ".")
    scanner_service.root_dir = workspace
    scanner_service.abs_path = os.path.abspath(workspace)

    snapshot = scanner_service.invoke()

    snapshot_lines = [
        f"Root Path: {snapshot.root_path}",
        f"Total Files: {snapshot.total_files}",
        f"Total Directories: {snapshot.total_directories}",
        "\nFiles:",
    ]
    for file in snapshot.files:
        snapshot_lines.append(
            f"- {file.path} ({file.lines_count} lines, {file.size_bytes} bytes)"
        )

    snapshot_lines.append("\nDirectories:")
    for directory in snapshot.directories:
        snapshot_lines.append(f"- {directory}")

    snapshot_text = "\n".join(snapshot_lines)

    return {"snapshot": snapshot_text}


def agent(state: KaizenState) -> dict:
    """
    LLM node. Primary autonomous reasoning loop.
    """
    return coder_service.invoke(state)
