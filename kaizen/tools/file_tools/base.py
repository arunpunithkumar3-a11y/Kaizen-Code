from pathlib import Path


def path_resolver(workspace: str, path: str) -> Path:
    workspace_path = Path(workspace).resolve()
    requested_path = Path(path)

    if requested_path.is_absolute():
        resolved_path = requested_path.resolve()
    else:
        resolved_path = (workspace_path / requested_path).resolve()

    if resolved_path.is_relative_to(workspace_path):
        return resolved_path
    else:
        raise PermissionError("Access outside workspace is prohibited.")
