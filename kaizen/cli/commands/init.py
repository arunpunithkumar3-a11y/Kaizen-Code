from kaizen.config.env_manager import EnvironmentManager
from kaizen.config.manager import ConfigManager
from kaizen.config.models import KaizenConfig, LLMConfig
from kaizen.config.validator import ConfigValidator
from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console
from kaizen.cli.ui.panels import error, show_banner, success
from kaizen.cli.ui.prompts import prompt_api_key, prompt_model, prompt_provider


def build_config(provider: str, model: str) -> KaizenConfig:

    return KaizenConfig(
        llm=LLMConfig(
            provider=provider,
            model=model,
        )
    )


def validate_config(config: KaizenConfig) -> None:

    validator = ConfigValidator()

    validator.validate(config)


def save_config(config: KaizenConfig) -> None:

    manager = ConfigManager()

    manager.save(config)


def save_api_key(provider: str, api_key: str | None) -> None:

    if api_key is None:
        return

    env_manager = EnvironmentManager()

    env_manager.set_api_key(
        provider=provider,
        api_key=api_key,
    )


def init() -> None:

    try:
        show_banner()

        provider = prompt_provider()

        model = prompt_model(provider)

        api_key = prompt_api_key(provider)

        config = build_config(
            provider=provider,
            model=model,
        )

        with console.status(
            "[bold #875fdf]Configuring and validating Kaizen...[/bold #875fdf]"
        ):
            save_config(config)

            save_api_key(provider, api_key)

            validate_config(config)

        success("Kaizen configured successfully!")

        console.print()

        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))

        table.add_row(
            "[bold #875fdf]🤖 LLM Provider[/bold #875fdf]", f"[white]{provider}[/white]"
        )

        table.add_row(
            "[bold #875fdf]⚙️ Model Name[/bold #875fdf]", f"[white]{model}[/white]"
        )

        if api_key is not None:
            table.add_row(
                "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                "[#00ff87]•••••••• (Stored)[/#00ff87]",
            )

        else:
            table.add_row(
                "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                "[#ffaf5f]None (Not required)[/#ffaf5f]",
            )

        summary_panel = Panel(
            table,
            title="[bold #00ff87] 🎛️ CONFIGURATION SUMMARY [/bold #00ff87]",
            border_style="#00ff87",
            box=box.ROUNDED,
            expand=False,
            padding=(1, 2),
        )

        console.print(summary_panel)

        console.print()

    except KeyboardInterrupt:
        console.print()

        error("Setup cancelled by user.")
