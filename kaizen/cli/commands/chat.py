from pathlib import Path

from langchain_core.messages import HumanMessage
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console

from kaizen.core.engine.graph import builder
from kaizen.storage.db.session_manager import session_service
from kaizen.storage.paths import KAIZEN_HOME
from kaizen.cli.ui import panels

console = Console()


def chat():
    import questionary
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE
    
    console.print("\n[bold #875fdf]💬 Start a New Chat Session[/bold #875fdf]")
    title = questionary.text(
        "Enter title for this session:",
        default="New Chat",
        style=QUESTIONARY_STYLE
    ).ask()
    
    if title is None:
        return
        
    title = title.strip() or "New Chat"
    thread_id = session_service.create(title=title)
    
    history_file = KAIZEN_HOME / "history.txt"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(history=FileHistory(str(history_file)))
    
    while True:
        try:
            query = session.prompt(
                HTML("<style fg='#875fdf'><b>kaizen</b></style><style fg='#00d7ff'><b> &gt; </b></style>"),
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
