import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

os.environ["KAIZEN_PROVIDER"] = "nvidia"
os.environ["KAIZEN_MODEL"] = "nvidia/nemotron-3-ultra-550b-a55b"
os.environ["NVIDIA_API_KEY"] = (
    "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"
)


from kaizen.core.engine.graph import builder

query = """
Build an AI Expense Tracker.

Features:
- Authentication
- Dashboard
- Income/Expense CRUD
- Monthly analytics
- Charts
- AI insights using an LLM
- CSV export
- PDF reports
- Categories
- Search
- Filters
- REST API
- React frontend
- FastAPI backend
- PostgreSQL
"""


workspace_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_agent_workspace")
)


from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    result = builder.invoke(
        {
            "messages": [HumanMessage(content=query)],
            "workspace": workspace_dir,
        },
        config={"configurable": {"thread_id": "10"}},
    )

    print(result["messages"][-1].content)
