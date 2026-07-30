from rich.console import Console

from kaizen.storage.manager import storage_manager

console = Console()


def init():
    console.print("[bold #875fdf]Initializing Kaizen Code...[/bold #875fdf]")
    storage_manager.initialize()
    console.print("[bold #00ff87]Initialization Complete[/bold #00ff87]")
