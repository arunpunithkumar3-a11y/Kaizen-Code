from typing import List, Literal

from pydantic import BaseModel, Field


class TodoItem(BaseModel):
    """Represents a single atomic engineering or research sub-task inside the agent's plan."""

    task: str = Field(
        description="The detailed description of what engineering action needs to be performed."
    )
    status: Literal["pending", "in_progress", "completed"] = Field(
        default="pending",
        description="The active status tracker for this step. Update to 'completed' when an action succeeds.",
    )


class WriteTodosInput(BaseModel):
    """The complete, ordered checklist defining the current operational roadmap for the task."""

    todos: List[TodoItem] = Field(
        description="The full array of tasks. Always provide the entire updated list when changing any single task status."
    )
