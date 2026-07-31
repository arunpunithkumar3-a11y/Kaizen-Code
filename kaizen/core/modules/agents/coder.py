from dotenv import load_dotenv

from kaizen.core.engine.llm import get_llm
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
from kaizen.tools.web_search_tool.tool import web_search_tool

load_dotenv()


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
            web_search_tool,
        ]

    def invoke(self, state: KaizenState) -> dict:
        llm = get_llm()

        llm_with_tools = llm.bind_tools(self.tools)

        chain = SYSTEM_PROMPT | llm_with_tools
        response = chain.invoke(
            {
                "snapshot": state.get("snapshot", "No snapshot available."),
                "messages": list(state["messages"]),
            }
        )

        return {"messages": [response]}
