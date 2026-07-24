import platform
import sys

from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console


def version() -> None:
    """Display Kaizen Code version and system environment info."""

    sys_table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))

    arch_info = f"{platform.machine()} ({platform.architecture()[0]})"

    sys_table.add_row(
        "[bold #875fdf]Kaizen Code version[/bold #875fdf]", "[white]v0.1.0[/white]"
    )

    sys_table.add_row(
        "[bold #875fdf]Python version[/bold #875fdf]",
        f"[white]{sys.version.split()[0]}[/white]",
    )

    sys_table.add_row(
        "[bold #875fdf]Platform[/bold #875fdf]",
        f"[white]{platform.system()} {platform.release()}[/white]",
    )

    sys_table.add_row(
        "[bold #875fdf]Architecture[/bold #875fdf]", f"[white]{arch_info}[/white]"
    )

    panel = Panel(
        sys_table,
        title="[bold #875fdf]⚙️ Kaizen Code System Information[/bold #875fdf]",
        border_style="#875fdf",
        box=box.ROUNDED,
        expand=False,
        padding=(1, 2),
    )

    console.print(panel)
