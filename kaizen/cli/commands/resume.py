from pathlib import Path

import questionary
from langchain_core.messages import HumanMessage
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from questionary import Choice
from rich.console import Console

from kaizen.cli.ui import panels
from kaizen.cli.ui.styles import QUESTIONARY_STYLE
from kaizen.core.engine.graph import builder
from kaizen.storage.db.session_manager import session_service
from kaizen.storage.paths import KAIZEN_HOME

console = Console()


def resume():
    data = [
        Choice(y["title"], value=x) for x, y in session_service.list_sessions().items()
    ]
    thread_id = questionary.select(
        "Choose Chats", choices=data, style=QUESTIONARY_STYLE
    ).ask()
    if thread_id is None:
        return

    history_file = KAIZEN_HOME / "history.txt"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(history=FileHistory(str(history_file)))

    while True:
        try:
            query = session.prompt(
                HTML(
                    "<style fg='#875fdf'><b>kaizen</b></style><style fg='#00d7ff'><b> &gt; </b></style>"
                ),
                auto_suggest=AutoSuggestFromHistory(),
            ).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not query:
            continue
        if query == "exit":
            break

        with console.status("[bold #875fdf]Thinking...[/bold #875fdf]"):
            result = builder.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "workspace": Path.cwd(),
                },
                config={"configurable": {"thread_id": thread_id}},
            )

        content = result["messages"][-1].content
        panels.parse_and_render_agent_message(content)
