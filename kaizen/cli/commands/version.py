import platform
import sys

from rich.table import Table

from kaizen.cli.ui.console import console
from kaizen.cli.ui import panels


def version() -> None:
    """Display Kaizen Code version and system environment info."""
    panels.show_banner()
    sys_table = Table(show_header=False, box=None, padding=(0, 4, 0, 0))

    arch_info = f"{platform.machine()} ({platform.architecture()[0]})"

    sys_table.add_row("[dim]Kaizen Code[/dim]", "v0.1.0")
    sys_table.add_row("[dim]Python[/dim]", sys.version.split()[0])
    sys_table.add_row("[dim]Platform[/dim]", f"{platform.system()} {platform.release()}")
    sys_table.add_row("[dim]Architecture[/dim]", arch_info)

    console.print()
    console.print(sys_table)
    console.print()

