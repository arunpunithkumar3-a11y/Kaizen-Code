import os
import json
from pydantic import BaseModel

class Config(BaseModel):
    project_name: str
    version: int
    paths: list[str]

def load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = json.load(f)
    return Config(**data)

def scan_directory(base_path: str, rel_path: str):
    abs_path = os.path.join(base_path, rel_path)
    files = []
    for root, dirs, filenames in os.walk(abs_path):
        for name in filenames:
            files.append(os.path.join(root, name))
    return files

def main():
    try:
        config = load_config("config.json")
    except FileNotFoundError:
        print("Error: config.json not found")
        return

    print("Loaded config:", config)

    if not config.paths:
        print("Error: no paths configured in config.json")
        return

    files = scan_directory(config.paths[0], os.getcwd())
    print("Found files:", files)

if __name__ == "__main__":
    main()
