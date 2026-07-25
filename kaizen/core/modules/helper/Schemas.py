from pydantic import BaseModel


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
