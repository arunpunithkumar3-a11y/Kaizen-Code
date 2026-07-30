import os

from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from kaizen.core.engine.state import KaizenState
from kaizen.core.modules.agents.coder import CoderService
from kaizen.core.modules.agents.scanner import ScannerService
from kaizen.core.modules.helper.memory import memory_cleaner
from kaizen.tools.file_tools.edit_file_tool import edit_file
from kaizen.tools.file_tools.list_dir_tool import list_directory
from kaizen.tools.file_tools.read_file_tool import read_file
from kaizen.tools.file_tools.write_file_tool import write_file
from kaizen.tools.ripgrep_tool.tool import ripgrep
from kaizen.tools.subagents.subagent_tool import subagent_tool
from kaizen.tools.Terminal.terminal_tool import terminal
from kaizen.tools.todo.todo import write_todos
from kaizen.tools.web_search_tool.tool import web_search_tool

DANGEROUS_TOOLS = ["edit_file", "write_file", "terminal"]
# Developer Agent tools
developer_tools = [
    read_file,
    write_file,
    edit_file,
    list_directory,
    ripgrep,
    terminal,
    write_todos,
    subagent_tool,
    web_search_tool,
]

# Built-in LangGraph ToolNode instance, mapped to state's messages key
tool_node = ToolNode(developer_tools, messages_key="messages")

coder_service = CoderService()
scanner_service = ScannerService()


def scanner(state: KaizenState) -> dict:
    """
    Scanner node. Scans the workspace directory and saves a snapshot to the state.
    """
    from kaizen.cli.ui import panels

    if state.get("snapshot"):
        return {}
    panels.log_tool_start("Scanning", "workspace")
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

    panels.log_tool_end(
        "Scanned",
        "project files",
        success=True,
        details=f"{snapshot.total_files} files, {snapshot.total_directories} dirs",
    )
    return {"snapshot": snapshot_text}


def agent(state: KaizenState) -> dict:
    """
    LLM node. Primary autonomous reasoning loop.
    """
    memory_cleaner(state)
    return coder_service.invoke(state)


def approval_node(state: KaizenState):
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
    tool_calls = last_message.tool_calls
    dangerous_calls = []
    for tool_call in tool_calls:
        name = tool_call["name"]
        is_dangerous = False
        for dt in DANGEROUS_TOOLS:
            if name == dt or name.endswith("__" + dt) or name.endswith("_" + dt):
                is_dangerous = True
                break
        if is_dangerous:
            args = tool_call["args"]
            clean_args = {}
            if "path" in args:
                clean_args = {"path": args["path"]}
            else:
                clean_args = args
            dangerous_calls.append(
                {"tool": tool_call["name"], "args": clean_args}
            )
    if not dangerous_calls:
        return {}
    approval = interrupt({"type": "tool_approval", "tool_calls": dangerous_calls})
    if not approval.get("approved"):
        tool_messages = []
        for tool_call in tool_calls:
            tool_messages.append(
                ToolMessage(
                    content=f"Execution rejected by user. Feedback: {approval.get('feedback', 'No feedback provided.')}",
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": tool_messages}
    return {}


def route_after_approval(state: KaizenState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, ToolMessage):
        return "agent"
    return "tools"
