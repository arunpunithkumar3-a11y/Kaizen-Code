from pydantic import BaseModel, Field







class TerminalInput(BaseModel):
    command: str = Field(
        description=(
            "Shell command to execute inside the workspace (e.g., 'pytest', 'python -m py_compile app/main.py'). "
            "DO NOT run persistent web servers like uvicorn, flask, or npm start as terminal execution is synchronous."
        )
    )






