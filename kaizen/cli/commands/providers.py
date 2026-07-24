from kaizen.config.constants import PROVIDERS
from kaizen.config.env_manager import EnvironmentManager
from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console


def providers() -> None:
    """List available LLM providers and their configuration status."""

    env_manager = EnvironmentManager()

    table = Table(box=box.SIMPLE, header_style="bold #875fdf")

    table.add_column("Provider", style="white")

    table.add_column("API Key Required", justify="center")

    table.add_column("Status", justify="left")

    for provider_id, metadata in PROVIDERS.items():
        req_key = (
            "[white]Yes[/white]"
            if metadata.requires_api_key
            else "[dim white]No[/dim white]"
        )

        if metadata.requires_api_key:
            if env_manager.has_api_key(provider_id):
                status = "[#00ff87]Configured[/#00ff87]"

            else:
                status = "[#ff5f87]Missing[/#ff5f87]"

        else:
            status = "[#8a8a8a]Not Required[/#8a8a8a]"

        table.add_row(provider_id, req_key, status)

    panel = Panel(
        table,
        title="[bold #875fdf]🤖 LLM Providers[/bold #875fdf]",
        border_style="#875fdf",
        box=box.ROUNDED,
        expand=False,
        padding=(1, 2),
    )

    console.print(panel)
