import os

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI

from kaizen.core.engine.state import KaizenState

load_dotenv()


LLM = ChatOpenAI(
    model=os.getenv("KAIZEN_MODEL"),
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=1,
    top_p=1,
    max_completion_tokens=16384,
)

INITIAL_SUMMARY_PROMPT = """You are a memory consolidation module for an AI software engineering agent. 
Your task is to analyze the following sequence of conversation events and generate a concise, structured Markdown summary of what has been done so far.

Focus only on:
1. The user's original objective.
2. Which files were read/inspected.
3. Which files were modified (and what changes were made).
4. The outcome of any execution tests or compiler checks (specifically details of any errors encountered).

Conversation Events:
{events}

Output your response as a clean, bulleted Markdown summary. Do not include introductory text or markdown formatting blocks (e.g., do not start with ```markdown). Keep it under 150 words.
"""

INCREMENTAL_SUMMARY_PROMPT = """You are a memory consolidation module for an AI software engineering agent.
Your task is to merge the sequence of new conversation events into the existing workspace summary to create a single, cohesive, up-to-date Markdown summary.

Guidelines:
1. Maintain chronological order of events.
2. If a file was modified multiple times, consolidate the changes rather than listing each edit separately.
3. Keep the summary highly dense and concise. Do not let the overall summary grow excessively long.
4. Ensure any active, unresolved errors or failing tests from the new events are highlighted at the end of the summary.

Existing Workspace Summary:
{existing_summary}

New Conversation Events:
{events}

Output the updated, consolidated summary as a clean, bulleted Markdown list. Do not include introductory text or markdown formatting blocks (e.g., do not start with ```markdown). Keep it under 200 words.
"""


def memory_cleaner(state: KaizenState):
    events_lines = []
    if not len(state["messages"]) > 50:
        return {}

    messages_to_delete = state["messages"][:30]
    messages_to_keep = state["messages"][30:]

    for msg in messages_to_delete:
        if isinstance(msg, ToolMessage):
            continue

        if isinstance(msg, HumanMessage):
            events_lines.append(f"User: {msg.content}")

        elif isinstance(msg, AIMessage):
            # Capture tool usage intention if present
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tools = ", ".join([tc["name"] for tc in msg.tool_calls])
                events_lines.append(f"Agent initiated tools: [{tools}]")
            else:
                events_lines.append(f"Agent: {msg.content}")

    new_events = "\n".join(events_lines)
    existing_summary = state.get("summary", "")

    # Run LLM summarization if there are events to compile
    if not new_events.strip():
        new_summary = existing_summary
    else:
        if not existing_summary:
            prompt = INITIAL_SUMMARY_PROMPT.format(events=new_events)
        else:
            prompt = INCREMENTAL_SUMMARY_PROMPT.format(
                existing_summary=existing_summary, events=new_events
            )

        try:
            response = LLM.invoke(prompt)
            new_summary = response.content.strip()
        except Exception as e:
            print(f"⚠️ [Memory Cleaner] Warning: Summarizer call failed: {e}")
            new_summary = existing_summary

    summary_msg = SystemMessage(
        content=f"### SUMMARY OF COMPLETED ACTIONS:\n{new_summary}",
        id="workspace_summary",
    )

    all_removals = [RemoveMessage(id=m.id) for m in state["messages"] if m.id]

    new_active_stack = [summary_msg] + messages_to_keep

    return {"messages": all_removals + new_active_stack, "summary": new_summary}
