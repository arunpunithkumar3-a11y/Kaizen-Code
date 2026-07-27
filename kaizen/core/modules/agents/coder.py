import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from kaizen.core.engine.state import KaizenState
from kaizen.core.modules.agents.backend import ServiceClass
from kaizen.core.modules.helper.prompts import SYSTEM_PROMPT
from kaizen.tools.file_tools.edit_file_tool import edit_file
from kaizen.tools.file_tools.list_dir_tool import list_directory
from kaizen.tools.file_tools.read_file_tool import read_file
from kaizen.tools.file_tools.write_file_tool import write_file
from kaizen.tools.ripgrep_tool.tool import ripgrep
from kaizen.tools.subagents.subagent_tool import subagent_tool
from kaizen.tools.Terminal.terminal_tool import terminal
from kaizen.tools.todo.todo import write_todos

load_dotenv()

LLM = ChatOpenAI(
    model=os.getenv("KAIZEN_MODEL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=1,
    top_p=1,
    max_completion_tokens=16384,
)


class CoderService(ServiceClass):
    def __init__(self):
        self.tools = [
            read_file,
            write_file,
            edit_file,
            list_directory,
            ripgrep,
            terminal,
            write_todos,
            subagent_tool,
        ]

    def invoke(self, state: KaizenState) -> dict:
        print("\n🤖 [Kaizen Agent] Thinking...")
        os.environ["WORKSPACE"] = state["workspace"]
        llm = LLM

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(self.tools)

        # Construct and invoke LCEL chain
        chain = SYSTEM_PROMPT | llm_with_tools
        response = chain.invoke(
            {
                "snapshot": state.get("snapshot", "No snapshot available."),
                "messages": list(state["messages"]),
            }
        )

        return {"messages": [response]}
