from typing import List

from langchain_core.tools import tool

from kaizen.tools.todo.schemas import TodoItem, WriteTodosInput


@tool(args_schema=WriteTodosInput)
def write_todos(todos: List[TodoItem]) -> dict:
    print("creating todos")
    """Manage and maintain a structured todo list. Use this tool to plan complex
    requests, track progress, or adapt the execution strategy when encountering blockers.
    """

    serialized_todos = [item.model_dump() for item in todos]
    return {"todos": serialized_todos}
