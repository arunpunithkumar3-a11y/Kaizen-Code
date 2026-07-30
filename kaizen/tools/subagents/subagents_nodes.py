import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Send

from kaizen.core.modules.helper.prompts import SUBAGENT_SYSTEM_PROMPT
from kaizen.tools.file_tools.edit_file_tool import edit_file
from kaizen.tools.file_tools.list_dir_tool import list_directory
from kaizen.tools.file_tools.read_file_tool import read_file
from kaizen.tools.file_tools.write_file_tool import write_file
from kaizen.tools.ripgrep_tool.tool import ripgrep
from kaizen.tools.subagents.subagent_state import KaizenSubAgentState, KaizenWorkerState
from kaizen.tools.Terminal.terminal_tool import terminal
from kaizen.tools.todo.todo import write_todos
from kaizen.tools.web_search_tool.tool import web_search_tool

load_dotenv()


LLM = ChatOpenAI(
    model=os.getenv("KAIZEN_MODEL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=1,
    top_p=1,
    max_completion_tokens=16384,
)


developer_tools = [
    read_file,
    write_file,
    edit_file,
    list_directory,
    ripgrep,
    terminal,
    write_todos,
    web_search_tool,
]


tool_node = ToolNode(developer_tools, messages_key="messages")
llm_with_tools = LLM.bind_tools(developer_tools)


def subagent(state: KaizenWorkerState):
    os.environ["WORKSPACE"] = state["workspace"]
    chain = SUBAGENT_SYSTEM_PROMPT | llm_with_tools
    result = chain.invoke(
        {
            "snapshot": state.get("snapshot", "No snapshot available."),
            "task": state.get("task", "No task assigned."),
            "messages": list(state["messages"]),
        }
    )
    return {"messages": [result]}


def finish(state: KaizenWorkerState):
    return {"report": [state["messages"][-1]]}


graph1 = StateGraph(KaizenWorkerState)
graph1.add_node("subagent", subagent)
graph1.add_node("tool_node", tool_node)
graph1.add_node("finish_task", finish)
graph1.add_edge(START, "subagent")
graph1.add_conditional_edges(
    "subagent", tools_condition, {"tools": "tool_node", "__end__": "finish_task"}
)
graph1.add_edge("tool_node", "subagent")
graph1.add_edge("finish_task", END)
subagent_graph = graph1.compile()


def spawn_node(state: KaizenSubAgentState):
    return {}


def spawn_agents(state: KaizenSubAgentState):
    sends = []
    for task in state["tasks"]:
        sends.append(
            Send(
                "worker",
                {
                    "messages": [
                        HumanMessage(
                            content=f"Please execute the assigned subtask:\n{task}"
                        )
                    ],
                    "workspace": state["workspace"],
                    "snapshot": state["snapshot"],
                    "task": task,
                    "report": [],
                },
            )
        )
    return sends


def run_worker(state: KaizenWorkerState):
    result = subagent_graph.invoke(state)
    return {"reports": result["report"]}


coordinator = StateGraph(KaizenSubAgentState)

coordinator.add_node("spawn", spawn_node)
coordinator.add_node("worker", run_worker)

coordinator.add_edge(START, "spawn")
coordinator.add_conditional_edges("spawn", spawn_agents)
coordinator.add_edge("worker", END)

subagents_graph = coordinator.compile()
