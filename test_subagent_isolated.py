import os

from dotenv import load_dotenv

from kaizen.tools.subagents.subagent_tool import subagent_tool

# Load the environment variables from .env
load_dotenv()

# Resolve the path to the test workspace
workspace_dir = os.path.abspath("./test_agent_workspace")

# Simple tasks for the subagent to execute
tasks = [
    "Check if config.json exists in the workspace and print its content.",
    "Read main.py and list the class and function names."
]

print("Spawning subagents in parallel to execute tasks...")
for idx, t in enumerate(tasks):
    print(f"  - Task {idx + 1}: {t}")


# Invoke the subagent tool directly via its underlying function
result = subagent_tool.func(
    tasks=tasks,
    workspace=workspace_dir,
    snapshot="Workspace has config.json and main.py",
)

print("\n--- Consolidated Subagent Report ---")
print(result)
