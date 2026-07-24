from typing import Optional

from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    path: str = Field(description="Relative file path inside the workspace.")

    start_line: Optional[int] = Field(
        default=None, ge=1, description="1-indexed line number to start reading from."
    )

    end_line: Optional[int] = Field(
        default=None,
        ge=1,
        description="1-indexed line number to stop reading at (inclusive).",
    )


class EditFileInput(BaseModel):
    path: str = Field(description="Relative file path inside the workspace.")

    old_text: str = Field(
        description="Exact text block to replace. Must match the file content exactly."
    )

    new_text: str = Field(description="Replacement text block.")

    replace_all: bool = Field(
        default=False,
        description="Replace all occurrences of old_text instead of just the first occurrence.",
    )


class WriteFileInput(BaseModel):
    path: str = Field(description="Relative file path inside the workspace.")

    content: str = Field(description="Complete file content to write.")


class ListDirectoryInput(BaseModel):
    path: str = Field(
        default=".",
        description="Relative directory inside the workspace (e.g. '.', 'src').",
    )
