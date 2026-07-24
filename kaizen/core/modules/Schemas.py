from pydantic import BaseModel, Field

class Task(BaseModel):
    id: int
    title: str
    description: str
    success_criteria: str

class ExecutionPlan(BaseModel):
    tasks: list[Task] = Field(description="Ordered list of tasks to complete sequentially.")

class SearchResult(BaseModel):
    path: str
    line: int
    preview: str

class FileInfo(BaseModel):
    path: str
    extension: str
    size_bytes: int
    lines_count: int

class ProjectSnapshot(BaseModel):
    root_path: str
    files: list[FileInfo]
    directories: list[str]
    total_files: int
    total_directories: int

