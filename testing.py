import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from kaizen.core.engine.graph import builder

query = """
thank you bro
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
        config={"configurable": {"thread_id": "punith"}},
    )

    print(result["messages"][-1].content)
