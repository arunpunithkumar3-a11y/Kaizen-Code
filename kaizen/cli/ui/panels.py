from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
import json
import re
from pathlib import Path

from kaizen.cli.ui.console import console

BANNER_LINES = [
    (
        r" ██╗  ██╗  █████╗  ██╗███████╗███████╗███╗   ██╗     ██████╗  ██████╗ ██████╗ ███████╗",
        "#875fdf",
    ),
    (
        r" ██║ ██╔╝ ██╔══██╗ ██║╚══███╔╝██╔════╝████╗  ██║    ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝",
        "#7a76e7",
    ),
    (
        r" █████╔╝  ███████║ ██║  ███╔╝ █████╗  ██╔██╗ ██║    ██║      ██║   ██║██║  ██║█████╗  ",
        "#698eed",
    ),
    (
        r" ██╔═██╗  ██╔══██║ ██║ ███╔╝  ██╔══╝  ██║╚██╗██║    ██║      ██║   ██║██║  ██║██╔══╝  ",
        "#55a5f3",
    ),
    (
        r" ██║  ██╗ ██║  ██║ ██║███████╗███████╗██║ ╚████║    ╚██████╗ ╚██████╔╝██████╔╝███████╗",
        "#39bcf8",
    ),
    (
        r" ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝     ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝",
        "#00d7ff",
    ),
]


def show_banner() -> None:

    console.print()

    for line, color in BANNER_LINES:
        console.print(line, style=f"bold {color}")

    console.print(
        " [bold #875fdf]⚒ KAIZEN CODE[/bold #875fdf] | [bold #00d7ff]Next-Gen AI Coding Agent[/bold #00d7ff] [dim white]v0.1.0[/dim white]"
    )

    console.print(" " + "[#8a8a8a]━" * 87 + "[/#8a8a8a]")

    console.print()


def success(message: str) -> None:

    console.print(
        Panel(
            f" [bold #00ff87]✔ Success:[/bold #00ff87] {message}",
            border_style="#00ff87",
            box=box.ROUNDED,
            expand=False,
        )
    )


def error(message: str) -> None:

    console.print(
        Panel(
            f" [bold #ff5f87]✘ Error:[/bold #ff5f87] {message}",
            border_style="#ff5f87",
            box=box.ROUNDED,
            expand=False,
        )
    )


def warning(message: str) -> None:

    console.print(
        Panel(
            f" [bold #ffaf5f]⚠ Warning:[/bold #ffaf5f] {message}",
            border_style="#ffaf5f",
            box=box.ROUNDED,
            expand=False,
        )
    )


def info(message: str) -> None:

    console.print(
        Panel(
            f" [bold #5f87ff]ℹ Info:[/bold #5f87ff] {message}",
            border_style="#5f87ff",
            box=box.ROUNDED,
            expand=False,
        )
    )


def show_status_bar(model: str, base_url: str) -> None:
    workspace = str(Path.cwd())
    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")
    
    table.add_row(
        f"📂 [bold #875fdf]Workspace:[/bold #875fdf] [white]{workspace}[/white]",
        f"🤖 [bold #875fdf]Model:[/bold #875fdf] [white]{model}[/white] | 🌐 [bold #875fdf]URL:[/bold #875fdf] [white]{base_url}[/white]"
    )
    
    console.print(
        Panel(
            table,
            border_style="#875fdf",
            box=box.ROUNDED,
            expand=True,
            padding=(0, 2),
        )
    )


def render_tool_call(name: str, arguments: dict) -> None:
    args_str = ""
    if arguments:
        try:
            args_str = json.dumps(arguments, indent=2)
        except Exception:
            args_str = str(arguments)
            
    header = Text()
    header.append("🛠️  Calling Tool: ", style="bold #00d7ff")
    header.append(name, style="bold #875fdf")
    
    body = Text()
    if args_str:
        body.append(args_str, style="#5f87ff")
        
    console.print(
        Panel(
            body,
            title=header,
            title_align="left",
            border_style="#00d7ff",
            box=box.ROUNDED,
            expand=False,
            padding=(0, 2),
        )
    )


def render_tool_result(name: str, result: str, is_error: bool = False) -> None:
    header = Text()
    if is_error:
        header.append("❌ Tool Result (Error): ", style="bold #ff5f87")
    else:
        header.append("✅ Tool Result: ", style="bold #00ff87")
    header.append(name, style="bold #875fdf")
    
    display_result = result
    if len(result) > 1500:
        display_result = result[:1500] + "\n\n... [output truncated for readability] ..."
        
    console.print(
        Panel(
            display_result,
            title=header,
            title_align="left",
            border_style="#ff5f87" if is_error else "#00ff87",
            box=box.ROUNDED,
            expand=False,
            padding=(0, 2),
        )
    )


def parse_and_render_agent_message(content: str) -> None:
    if not content or not isinstance(content, str):
        return
        
    state_match = re.search(r"\[CURRENT WORKSPACE STATE\](.*?)(?=\[THOUGHT\]|\[ACTION\]|$)", content, re.DOTALL)
    thought_match = re.search(r"\[THOUGHT\]:(.*?)(?=\[ACTION\]|$)", content, re.DOTALL)
    action_match = re.search(r"\[ACTION\]:(.*)", content, re.DOTALL)
    
    if not state_match and not thought_match and not action_match:
        console.print(Markdown(content))
        return
        
    if state_match:
        state_text = state_match.group(1).strip()
        lines = [line.strip() for line in state_text.split("\n") if line.strip()]
        state_lines = []
        for line in lines:
            if line.startswith("- "):
                line = line[2:]
            parts = line.split(":", 1)
            if len(parts) == 2:
                state_lines.append(f"  [bold #875fdf]• {parts[0]}:[/bold #875fdf] [white]{parts[1].strip()}[/white]")
            else:
                state_lines.append(f"  [white]{line}[/white]")
                
        if state_lines:
            console.print(
                Panel(
                    "\n".join(state_lines),
                    title="[bold #875fdf]Current Workspace State[/bold #875fdf]",
                    title_align="left",
                    border_style="#875fdf",
                    box=box.ROUNDED,
                    expand=False,
                )
            )
        
    if thought_match:
        thought_text = thought_match.group(1).strip()
        if thought_text:
            console.print(
                Panel(
                    f"[italic white]{thought_text}[/italic white]",
                    title="[bold #5f87ff]Thought Process[/bold #5f87ff]",
                    title_align="left",
                    border_style="#5f87ff",
                    box=box.ROUNDED,
                    expand=False,
                )
            )
        
    if action_match:
        action_text = action_match.group(1).strip()
        if action_text:
            console.print("\n[bold #00ff87]Response:[/bold #00ff87]")
            console.print(Markdown(action_text))
    else:
        remaining = content
        if state_match:
            remaining = remaining.replace(state_match.group(0), "")
        if thought_match:
            remaining = remaining.replace(f"[THOUGHT]:{thought_match.group(1)}", "")
            remaining = remaining.replace(f"[THOUGHT]: {thought_match.group(1)}", "")
            # Just in case
            remaining = remaining.replace("[THOUGHT]:", "")
        remaining = remaining.replace("[CURRENT WORKSPACE STATE]", "")
        remaining = remaining.strip()
        if remaining:
            console.print("\n[bold #00ff87]Response:[/bold #00ff87]")
            console.print(Markdown(remaining))


