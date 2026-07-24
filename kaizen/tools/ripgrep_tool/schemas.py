from pydantic import BaseModel, Field


class RipgrepInput(BaseModel):
    pattern: str = Field(
        description="Text, function, class name, variable, or regex pattern to search for in the codebase."
    )
