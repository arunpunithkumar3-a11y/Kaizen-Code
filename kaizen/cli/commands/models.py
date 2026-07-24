from kaizen.config.constants import PROVIDERS
from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console


def models() -> None:
    """Display recommended models for each LLM provider."""

    table = Table(box=box.SIMPLE, header_style="bold #875fdf")

    table.add_column("Provider", style="white")

    table.add_column("Recommended Model", style="accent")

    for provider_id, metadata in PROVIDERS.items():
        rec_model = metadata.recommended_model or "[dim white]None[/dim white]"

        table.add_row(provider_id, rec_model)

    panel = Panel(
        table,
        title="[bold #875fdf]⚙️ Recommended Models[/bold #875fdf]",
        border_style="#875fdf",
        box=box.ROUNDED,
        expand=False,
        padding=(1, 2),
    )

    console.print(panel)
