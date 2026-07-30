import json
import os
import re
import sys
import threading
import time
from pathlib import Path

from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.table import Table
from rich import box

from kaizen.cli.ui.console import console

# Thread local storage to run subagent tools silently
thread_local = threading.local()


class StatusManager:
    def __init__(self):
        self.status = None
        self.is_running = False

    def set_status(self, status):
        self.status = status
        self.is_running = True

    def start(self):
        if self.status and not self.is_running:
            try:
                self.status.start()
            except Exception:
                pass
            self.is_running = True

    def stop(self):
        if self.status and self.is_running:
            try:
                self.status.stop()
            except Exception:
                pass
            self.is_running = False

    def update(self, text, spinner="dots", spinner_style="status.spinner"):
        if not self.status:
            return
        if not self.is_running:
            self.start()
        try:
            self.status.update(text, spinner=spinner, spinner_style=spinner_style)
        except Exception:
            pass


status_manager = StatusManager()
always_allow_guardrail = False


def show_banner() -> None:
    from kaizen.storage.config.config_manager import config_service
    
    # 1. Retrieve config details
    config_data = config_service.show_config()
    data = config_data.get("config", {})
    model = data.get("KAIZEN_MODEL", "Not Set")
    base_url = data.get("KAIZEN_BASE_URL", "Not Set")
    workspace = str(Path.cwd().resolve())
    
    # 2. Calculate dynamic panel widths based on current terminal columns
    term_width = console.width
    inside_width = max(40, term_width - 6)
    
    # Header: KAIZEN logo using modern typography style
    header_table = Table.grid(expand=True)
    header_table.add_column(justify="left")
    header_table.add_row("[bold #7c3aed]❖ K A I Z E N   C O D E[/bold #7c3aed]  [dim]v0.1.0[/dim]")
    header_table.add_row("[dim #6c7086]the autonomous agent that never stops improving[/dim #6c7086]")
    header_table.add_row("")
    
    # Info Columns
    info_table = Table.grid(expand=True)
    info_table.add_column(width=14, justify="left")
    info_table.add_column(justify="left")
    
    # Truncate values to fit the column width to prevent wrapping and layout breakage
    max_val_w = max(10, inside_width - 16)
    workspace_disp = workspace if len(workspace) <= max_val_w else "..." + workspace[-(max_val_w - 3):]
    model_disp = model if len(model) <= max_val_w else model[:max_val_w - 3] + "..."
    base_url_disp = base_url if len(base_url) <= max_val_w else base_url[:max_val_w - 3] + "..."

    info_table.add_row("[dim #94a3b8]Workspace :[/dim #94a3b8]", f"[bold #3b82f6]{workspace_disp}[/bold #3b82f6]")
    info_table.add_row("[dim #94a3b8]Model     :[/dim #94a3b8]", f"[bold #10b981]{model_disp}[/bold #10b981]")
    if base_url and base_url != "Not Set":
         info_table.add_row("[dim #94a3b8]Base URL  :[/dim #94a3b8]", f"[dim #6c7086]{base_url_disp}[/dim #6c7086]")
    
    # Divider line
    divider = Table.grid(expand=True)
    divider.add_row("[#475569]─" * inside_width + "[/#475569]")
    
    # Columns for Help & Tips
    help_table = Table.grid(expand=True)
    left_w = int(inside_width * 0.50)
    right_w = inside_width - left_w
    help_table.add_column(width=left_w, justify="left")
    help_table.add_column(width=right_w, justify="left")
    
    left_content = Table.grid(expand=True)
    left_content.add_column(justify="left")
    left_content.add_row("[bold #818cf8]Available Commands[/bold #818cf8]")
    left_content.add_row("  [bold #3b82f6]chat[/bold #3b82f6]    [dim]- Start a new session[/dim]")
    left_content.add_row("  [bold #3b82f6]resume[/bold #3b82f6]  [dim]- Resume a saved session[/dim]")
    left_content.add_row("  [bold #3b82f6]config[/bold #3b82f6]  [dim]- Configure agent settings[/dim]")
    left_content.add_row("  [bold #3b82f6]version[/bold #3b82f6] [dim]- Display version info[/dim]")
    
    right_content = Table.grid(expand=True)
    right_content.add_column(justify="left")
    right_content.add_row("[bold #f59e0b]Tips for Getting Started[/bold #f59e0b]")
    right_content.add_row("  [dim]• Ask the agent to write code, edit, or search[/dim]")
    right_content.add_row("  [dim]• Reference files in workspace using[/dim] [bold #22c55e]@filename[/bold #22c55e]")
    right_content.add_row("  [dim]• Type[/dim] [bold #ef4444]exit[/bold #ef4444] [dim]anytime to exit the chat[/dim]")
    
    help_table.add_row(left_content, right_content)
    
    group = Group(
        header_table,
        info_table,
        "",
        divider,
        "",
        help_table
    )
    
    panel = Panel(
        group,
        border_style="bold #7c3aed",
        box=box.ROUNDED,
        width=term_width,
        padding=(1, 2)
    )
    
    console.print(panel)
    
    line_init = Text("  >_ ", style="bold #a78bfa")
    line_init.append("Kaizen Code AI initialized. Systems online...", style="bold white")
    console.print(line_init)
    console.print()


def success(message: str) -> None:
    was_active = status_manager.is_running
    status_manager.stop()
    console.print(f" [bold #10b981]✓[/bold #10b981] {message}")
    if was_active:
        status_manager.start()


def error(message: str) -> None:
    was_active = status_manager.is_running
    status_manager.stop()
    console.print(f" [bold #ef4444]✗[/bold #ef4444] {message}")
    if was_active:
        status_manager.start()


def warning(message: str) -> None:
    was_active = status_manager.is_running
    status_manager.stop()
    console.print(f" [bold #f59e0b]⚠[/bold #f59e0b] {message}")
    if was_active:
        status_manager.start()


def info(message: str) -> None:
    was_active = status_manager.is_running
    status_manager.stop()
    console.print(f" [bold #3b82f6]ℹ[/bold #3b82f6] {message}")
    if was_active:
        status_manager.start()


def show_status_bar(model: str, base_url: str) -> None:
    workspace = str(Path.cwd())
    console.print(f"  [dim]Workspace:[/dim]  [white]{workspace}[/white]")
    console.print(f"  [dim]Model:[/dim]      [white]{model}[/white]")
    console.print(f"  [dim]Base URL:[/dim]   [white]{base_url}[/white]")
    console.print()


def log_action(action: str, target: str) -> None:
    if getattr(thread_local, "is_subagent", False):
        return
    was_active = status_manager.is_running
    status_manager.stop()
    color_map = {
        "Reading": "#6c7086",
        "Writing": "#10b981",
        "Editing": "#10b981",
        "Listing": "#6c7086",
        "Searching": "#3b82f6",
        "Running": "#6366f1",
        "Planning": "#7c3aed",
        "Subagents": "#7c3aed",
        "Scanning": "#6c7086",
        "Success": "#10b981",
        "Failed": "#ef4444",
    }
    color = color_map.get(action, "#b4befe")
    action_padded = f"{action:>12}"
    console.print(
        f"[bold {color}]{action_padded}[/bold {color}]  [white]{target}[/white]"
    )
    if was_active:
        status_manager.start()


def log_tool_start(action: str, target: str) -> None:
    if getattr(thread_local, "is_subagent", False):
        return
    if status_manager.status:
        # Phase 2: Workspace Scans & Reads (yellow spinner)
        if action in ("Reading", "Listing", "Scanning"):
            status_manager.update(
                f"[yellow]Reading Workspace Files ({target})...[/yellow]",
                spinner="line",
                spinner_style="yellow",
            )
        # Phase 2: Searching Workspace
        elif action in ("Searching",):
            status_manager.update(
                f"[yellow]Searching Workspace Files ({target})...[/yellow]",
                spinner="line",
                spinner_style="yellow",
            )
        # Phase 3: External command executions (cyan spinner)
        elif action in ("Running",):
            status_manager.update(
                f"[cyan]Executing Command ({target})...[/cyan]",
                spinner="pipe",
                spinner_style="cyan",
            )
        # Phase 4: Patching code (green spinner)
        elif action in ("Writing", "Editing"):
            status_manager.update(
                f"[green]Applying Code Patches ({target})...[/green]",
                spinner="simpleDotsScrolling",
                spinner_style="green",
            )
        # Default/Phase 1: Thinking
        else:
            status_manager.update(
                f"[magenta]Thinking ({action} {target})...[/magenta]",
                spinner="dots",
                spinner_style="magenta",
            )
    else:
        log_action(action, target)


def log_tool_end(
    action: str, target: str, success: bool = True, details: str = None
) -> None:
    if getattr(thread_local, "is_subagent", False):
        return
    
    status_manager.stop()
    
    icon = (
        "[bold #10b981]✓[/bold #10b981]"
        if success
        else "[bold #ef4444]✗[/bold #ef4444]"
    )
    details_str = f" [dim]({details})[/dim]" if details else ""

    color_map = {
        "Read": "#6c7086",
        "Wrote": "#10b981",
        "Edited": "#10b981",
        "Listed": "#6c7086",
        "Searched": "#3b82f6",
        "Ran": "#6366f1",
        "Planned": "#7c3aed",
        "Subagents": "#7c3aed",
        "Scanned": "#6c7086",
    }
    color = color_map.get(action, "#b4befe")

    # Print clean line with single-space alignment
    console.print(
        f" {icon} [bold {color}]{action}[/bold {color}] [white]{target}[/white]{details_str}"
    )

    # Restore default spinner state
    status_manager.update(
        "[dim]Thinking...[/dim]",
        spinner="dots",
        spinner_style="status.spinner",
    )


def log_terminal_result(
    command: str, success: bool, output: str = None, exit_code: int = 0
) -> None:
    if getattr(thread_local, "is_subagent", False):
        return

    status_manager.stop()

    icon = (
        "[bold #10b981]✓[/bold #10b981]"
        if success
        else "[bold #ef4444]✗[/bold #ef4444]"
    )

    # Render diagnostics drawer using Tree component if failed, else clean print
    if success:
        console.print(f" {icon} [bold #6366f1]Ran[/bold #6366f1] [white]{command}[/white]")
    else:
        tree = Tree(f" {icon} [bold #6366f1]Ran[/bold #6366f1] [white]{command}[/white] [dim](failed exit {exit_code})[/dim]")
        if output:
            lines = output.strip().split("\n")
            max_lines = 15
            diag_node = tree.add("[dim]Diagnostics / Output[/dim]")
            for line in lines[:max_lines]:
                diag_node.add(Text(line, style="dim"))
            if len(lines) > max_lines:
                diag_node.add(
                    f"[dim]... ({len(lines) - max_lines} lines truncated) ...[/dim]"
                )
        console.print(tree)

    status_manager.update(
        "[dim]Thinking...[/dim]",
        spinner="dots",
        spinner_style="status.spinner",
    )


def render_tool_call(name: str, arguments: dict) -> None:
    args_str = ""
    if arguments:
        try:
            args_str = json.dumps(arguments)
        except Exception:
            args_str = str(arguments)
    log_tool_start("Tool Call", f"{name} {args_str}")


def render_tool_result(name: str, result: str, is_error: bool = False) -> None:
    status = "Failed" if is_error else "Success"
    log_tool_end(status, f"{name}", success=not is_error)


def parse_and_render_agent_message(content: str) -> None:
    if not content or not isinstance(content, str):
        return

    state_match = re.search(
        r"\[CURRENT WORKSPACE STATE\](.*?)(?=\[THOUGHT\]|\[ACTION\]|$)",
        content,
        re.DOTALL,
    )
    thought_match = re.search(r"\[THOUGHT\]:(.*?)(?=\[ACTION\]|$)", content, re.DOTALL)
    action_match = re.search(r"\[ACTION\]:(.*)", content, re.DOTALL)

    response_text = ""
    thought_text = ""
    if thought_match:
        thought_text = thought_match.group(1).strip()
        
        transition_pattern = r"(Respond (directly )?to the user( directly)?\.*?|Respond directly\.*?)"
        transition_match = re.search(transition_pattern, thought_text, re.IGNORECASE)
        if transition_match:
            split_idx = transition_match.start()
            response_text = thought_text[split_idx + len(transition_match.group(0)):].strip()
            response_text = response_text.lstrip(" .:,-")
            thought_text = thought_text[:split_idx].strip()
        elif not action_match and "\n\n" in thought_text:
            parts = thought_text.split("\n\n", 1)
            thought_text = parts[0].strip()
            response_text = parts[1].strip()

    if thought_text:
        console.print("[bold #7c3aed]❖ Thinking Process:[/bold #7c3aed]")
        console.print(Padding(Text(thought_text, style="italic #6c7086"), (0, 2)))
        console.print()

    action_text = ""
    if action_match:
        action_text = action_match.group(1).strip()
    
    final_output = action_text or response_text
    if final_output:
        console.print("[bold #6366f1]❖ Kaizen:[/bold #6366f1]")
        console.print(Padding(Markdown(final_output), (0, 2)))
        console.print()
    else:
        remaining = content
        if state_match:
            remaining = remaining.replace(state_match.group(0), "")
        if thought_match:
            remaining = remaining.replace(f"[THOUGHT]:{thought_match.group(1)}", "")
            remaining = remaining.replace(f"[THOUGHT]: {thought_match.group(1)}", "")
            remaining = remaining.replace("[THOUGHT]:", "")
        remaining = remaining.replace("[CURRENT WORKSPACE STATE]", "").strip()
        if remaining:
            console.print("[bold #6366f1]❖ Kaizen:[/bold #6366f1]")
            console.print(Padding(Markdown(remaining), (0, 2)))
            console.print()


class AgentStreamRenderer:
    def __init__(self):
        self.buffer = ""
        self.thought_text = ""
        self.response_text = ""
        self.live = None
        self.fallback = False

        # For fallback printing
        self.thought_printed_len = 0
        self.response_printed_len = 0
        self.thought_header_printed = False
        self.response_header_printed = False

    def on_chunk(self, chunk: str):
        self.buffer += chunk
        
        # 1. Parse what we have so far
        # Find where [CURRENT WORKSPACE STATE] ends
        state_end_idx = 0
        thought_idx = self.buffer.find("[THOUGHT]")
        action_idx = self.buffer.find("[ACTION]")
        
        if "[CURRENT WORKSPACE STATE]" in self.buffer:
            if thought_idx != -1:
                state_end_idx = thought_idx
            elif action_idx != -1:
                state_end_idx = action_idx
            else:
                # Still only workspace state content, don't display
                return
        
        content_after_state = self.buffer[state_end_idx:]
        
        thought_tag_match = re.search(r"\[THOUGHT\]:?\s*", content_after_state)
        
        if thought_tag_match:
            thought_start = thought_tag_match.end()
            # Check if we have [ACTION]
            action_tag_match = re.search(r"\[ACTION\]:?\s*", content_after_state)
            if action_tag_match:
                thought_end = action_tag_match.start()
                self.thought_text = content_after_state[thought_start:thought_end].strip()
                self.response_text = content_after_state[action_tag_match.end():]
            else:
                # No [ACTION] tag yet. Let's see if there is a transition phrase or double newline.
                full_thought = content_after_state[thought_start:]
                transition_pattern = r"(Respond (directly )?to the user( directly)?\.*?|Respond directly\.*?)"
                transition_match = re.search(transition_pattern, full_thought, re.IGNORECASE)
                if transition_match:
                    split_idx = transition_match.start()
                    self.thought_text = full_thought[:split_idx].strip()
                    self.response_text = full_thought[split_idx + len(transition_match.group(0)):].strip()
                    self.response_text = self.response_text.lstrip(" .:,-")
                elif "\n\n" in full_thought:
                    parts = full_thought.split("\n\n", 1)
                    self.thought_text = parts[0].strip()
                    self.response_text = parts[1]
                else:
                    self.thought_text = full_thought.strip()
                    self.response_text = ""
        else:
            # Check if this might be the start of a [THOUGHT] tag
            potential_prefix = "[THOUGHT]"
            potential_prefix_state = "[CURRENT WORKSPACE STATE]"
            if any(potential_prefix.startswith(content_after_state) for potential_prefix in (potential_prefix, potential_prefix_state)):
                return
            self.thought_text = ""
            self.response_text = content_after_state

        if (self.thought_text or self.response_text) and not self.live and not self.fallback:
            status_manager.stop()
            try:
                self.live = Live(self.get_renderable(), console=console, auto_refresh=True, refresh_per_second=8, vertical_overflow="visible")
                self.live.start()
            except Exception:
                try:
                    self.live = Live(self.get_renderable(), console=console, auto_refresh=True, refresh_per_second=8)
                    self.live.start()
                except Exception:
                    self.fallback = True

        if self.live:
            self.live.update(self.get_renderable())
        else:
            # Fallback printing
            if self.thought_text:
                if not self.thought_header_printed:
                    console.print("\n[bold #7c3aed]❖ Thinking Process:[/bold #7c3aed]")
                    self.thought_header_printed = True
                
                new_thought = self.thought_text[self.thought_printed_len:]
                if new_thought:
                    console.print(Text(new_thought, style="italic #6c7086"), end="")
                    sys.stdout.flush()
                    self.thought_printed_len = len(self.thought_text)
                    
            if self.response_text:
                if not self.response_header_printed:
                    if self.thought_header_printed:
                        console.print()
                    console.print("\n[bold #6366f1]❖ Kaizen:[/bold #6366f1]")
                    self.response_header_printed = True
                    
                new_response = self.response_text[self.response_printed_len:]
                if new_response:
                    console.print(new_response, end="", markup=False, highlight=False)
                    sys.stdout.flush()
                    self.response_printed_len = len(self.response_text)

    def get_renderable(self):
        parts = []
        if self.thought_text:
            parts.append(Text("❖ Thinking Process", style="bold #7c3aed"))
            parts.append(Padding(Text(self.thought_text, style="italic #6c7086"), (0, 2)))
            
        if self.response_text:
            if self.thought_text:
                parts.append(Text(""))  # Spacer
            parts.append(Text("❖ Kaizen", style="bold #6366f1"))
            parts.append(Padding(Markdown(self.response_text), (0, 2)))
            
        return Group(*parts)

    def finalize(self):
        if self.live:
            try:
                self.live.stop()
            except Exception:
                pass
            self.live = None
        else:
            status_manager.stop()
            if self.fallback:
                console.print()  # Finalize stdout line
            else:
                parse_and_render_agent_message(self.buffer)


def get_workspace_files() -> list:
    files = []
    ignore_dirs = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "dist",
        "build",
    }
    for root, dirs, filenames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for filename in filenames:
            if filename.startswith(".") and filename not in (".env", ".gitignore"):
                continue
            path = Path(root) / filename
            try:
                rel = str(path.relative_to(".")).replace("\\", "/")
                files.append(rel)
            except Exception:
                pass
    return files


def custom_input(prompt_text: str = None) -> str:
    was_active = status_manager.is_running
    if was_active:
        try:
            status_manager.stop()
        except Exception:
            pass

    from prompt_toolkit import PromptSession
    from prompt_toolkit.styles import Style
    from prompt_toolkit.completion import Completer, Completion

    class FileCompleter(Completer):
        def __init__(self, files):
            self.files = files
            
        def get_completions(self, document, complete_event):
            text = document.text_before_cursor
            if "@" in text:
                parts = text.split("@")
                prefix = parts[-1]
                if " " not in prefix:
                    for filename in self.files:
                        if filename.lower().startswith(prefix.lower()):
                            yield Completion(
                                filename,
                                start_position=-len(prefix),
                                display=filename
                            )

    style = Style.from_dict({
        'spark': 'bold #a78bfa',
        'name': 'bold #3b82f6',
        'arrow': 'bold #6366f1',
    })
    
    if prompt_text is None:
        prompt_val = [
            ('class:spark', ' ❖ '),
            ('class:name', 'kaizen'),
            ('class:arrow', ' ❯ '),
        ]
    else:
        prompt_val = prompt_text

    workspace_files = get_workspace_files()
    completer = FileCompleter(workspace_files)
    
    session = PromptSession(style=style, reserve_space_for_menu=0)
    try:
        user_input = session.prompt(
            prompt_val,
            completer=completer
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return "exit"
    finally:
        if was_active:
            try:
                status_manager.start()
            except Exception:
                pass


def ask_safety_permission(tool_name: str, detail: str) -> str:
    was_active = status_manager.is_running
    status_manager.stop()

    import questionary
    from questionary import Choice
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE

    message = f"Safety Guardrail: tool '{tool_name}' wants to run:\n  {detail}\nApprove this execution?"

    try:
        choice = questionary.select(
            message,
            choices=[
                Choice("Yes", value="yes"),
                Choice("No", value="no"),
                Choice("Always Allow", value="always allow"),
                Choice("Edit Command", value="edit command"),
            ],
            style=QUESTIONARY_STYLE,
            qmark="  ❖",
            pointer="❯",
        ).ask()

        if choice is None:
            return "no"
        return choice
    except KeyboardInterrupt:
        return "no"
    finally:
        if was_active:
            try:
                status_manager.start()
            except Exception:
                pass


def check_safety_guardrail(tool_name: str, detail: str) -> str:
    global always_allow_guardrail
    if always_allow_guardrail:
        return "yes"

    choice = ask_safety_permission(tool_name, detail)
    if choice == "always allow":
        always_allow_guardrail = True
        return "yes"
    return choice


def prompt_edit_command(command: str) -> str:
    was_active = status_manager.is_running
    status_manager.stop()

    from prompt_toolkit import PromptSession
    from prompt_toolkit.styles import Style

    style = Style.from_dict({
        'prompt': 'bold #f59e0b',
    })
    
    prompt_val = [
        ('class:prompt', 'Edit command ❯ '),
    ]
    
    session = PromptSession(style=style)
    try:
        user_input = session.prompt(
            prompt_val,
            default=command
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        return command
    finally:
        if was_active:
            try:
                status_manager.start()
            except Exception:
                pass


def execute_agent(thread_id: str, query: str) -> None:
    from langgraph.types import Command
    from langchain_core.messages import HumanMessage
    from kaizen.core.engine.graph import builder
    import questionary
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE

    config = {"configurable": {"thread_id": thread_id}}
    
    current_inputs = {
        "messages": [HumanMessage(content=query)],
        "workspace": Path.cwd(),
    }

    while True:
        with console.status("[dim]Thinking...[/dim]", spinner="dots") as status:
            status_manager.set_status(status)
            renderer = AgentStreamRenderer()
            
            try:
                for event in builder.stream(
                    current_inputs,
                    config=config,
                    stream_mode="messages",
                ):
                    message, metadata = event
                    if metadata.get("langgraph_node") == "agent":
                        if message.content:
                            renderer.on_chunk(message.content)
            except Exception as e:
                renderer.finalize()
                error(f"Error during graph execution: {str(e)}")
                break
            finally:
                renderer.finalize()

        state = builder.get_state(config)
        if not state.next:
            break

        if state.next[0] == "approval":
            task = state.tasks[0]
            if not task.interrupts:
                current_inputs = None
                continue

            interrupt_val = task.interrupts[0].value
            tool_calls = interrupt_val.get("tool_calls", [])

            console.print(
                "\n[bold #f59e0b]❖ Security Check - Approval Required:[/bold #f59e0b]"
            )
            for tc in tool_calls:
                console.print(f"  Tool: [bold #7c3aed]{tc['tool']}[/bold #7c3aed]")
                # Format arguments elegantly
                args = tc.get("args", {})
                if isinstance(args, dict):
                    for k, v in args.items():
                        if isinstance(v, str) and ("\n" in v or len(v) > 60):
                            console.print(f"  [dim]{k}:[/dim]")
                            lang = ""
                            if k in ("code", "content"):
                                path = args.get('path', '') or args.get('target', '') or args.get('TargetFile', '')
                                if path:
                                    ext = Path(path).suffix.lstrip('.')
                                    if ext in ('py', 'js', 'ts', 'json', 'md', 'sh', 'bash', 'css', 'html'):
                                        lang = ext
                            elif k == "command":
                                lang = "bash"
                            
                            if lang:
                                code_block = f"```{lang}\n{v.strip()}\n```"
                                console.print(Padding(Markdown(code_block), (0, 4)))
                            else:
                                console.print(Padding(v.strip(), (0, 4)))
                        else:
                            console.print(f"  [dim]{k}:[/dim] [white]{v}[/white]")
                else:
                    console.print(f"  Arguments: {args}")
            console.print()

            approved_choice = questionary.select(
                "Approve this execution?",
                choices=["Yes", "No", "No, and provide feedback"],
                style=QUESTIONARY_STYLE,
                qmark="  ❖",
                pointer="❯",
            ).ask()

            if approved_choice is None:
                break

            if approved_choice == "Yes":
                current_inputs = Command(resume={"approved": True})
            elif approved_choice == "No":
                current_inputs = Command(
                    resume={"approved": False, "feedback": "Rejected by user."}
                )
            else:
                feedback = questionary.text(
                    "Enter feedback for the agent:",
                    style=QUESTIONARY_STYLE,
                    qmark="  ❖",
                ).ask()
                if feedback is None:
                    break
                current_inputs = Command(
                    resume={"approved": False, "feedback": feedback}
                )
        else:
            current_inputs = None
