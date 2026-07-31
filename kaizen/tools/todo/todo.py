from typing import List

from langchain_core.tools import tool

from kaizen.tools.todo.schemas import TodoItem, WriteTodosInput


@tool(args_schema=WriteTodosInput)
def write_todos(todos: List[TodoItem]) -> str:
    from kaizen.cli.ui import panels
    panels.log_tool_start("Planning", "checklist")

    serialized_todos = [item.model_dump() for item in todos]
    panels.log_tool_end("Planned", "checklist updated", success=True, details=f"{len(todos)} tasks")
    import json
    return json.dumps(serialized_todos)
