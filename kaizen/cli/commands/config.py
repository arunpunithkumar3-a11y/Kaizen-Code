import typer
from kaizen.config.constants import PROVIDERS
from kaizen.config.env_manager import EnvironmentManager
from kaizen.config.manager import ConfigManager
from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console
from kaizen.cli.ui.panels import error, info, success, warning
from kaizen.cli.ui.prompts import confirm, prompt_api_key, prompt_model, prompt_provider

config_app = typer.Typer(help="Manage Kaizen configuration settings")


@config_app.command("show")
def show() -> None:
    """Display the current configuration."""

    try:
        manager = ConfigManager()

        config = manager.load()

        provider = config.llm.provider

        model = config.llm.model

        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))

        table.add_row(
            "[bold #875fdf]🤖 LLM Provider[/bold #875fdf]",
            f"[white]{provider or '(Not set)'}[/white]",
        )

        table.add_row(
            "[bold #875fdf]⚙️ Model Name[/bold #875fdf]",
            f"[white]{model or '(Not set)'}[/white]",
        )

        if provider:
            metadata = PROVIDERS.get(provider.lower())

            if metadata:
                if metadata.requires_api_key:
                    env_manager = EnvironmentManager()

                    if env_manager.has_api_key(provider):
                        table.add_row(
                            "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                            "[#00ff87]•••••••• (Stored)[/#00ff87]",
                        )

                    else:
                        table.add_row(
                            "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                            "[#ff5f87]Missing (Required)[/#ff5f87]",
                        )

                else:
                    table.add_row(
                        "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                        "[#5f87ff]None (Not required)[/#5f87ff]",
                    )

            else:
                table.add_row(
                    "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                    "[#ffaf5f]Unknown Provider[/#ffaf5f]",
                )

        else:
            table.add_row(
                "[bold #875fdf]🔑 API Credentials[/bold #875fdf]",
                "[#ffaf5f]None (No provider set)[/#ffaf5f]",
            )

        panel = Panel(
            table,
            title="[bold #875fdf] 🎛️ FORGEX CONFIGURATION [/bold #875fdf]",
            border_style="#875fdf",
            box=box.ROUNDED,
            expand=False,
            padding=(1, 2),
        )

        console.print(panel)

    except Exception as e:
        error(f"Failed to load configuration: {e}")


@config_app.command("provider")
def provider_cmd() -> None:
    """Interactively change the configured LLM provider."""

    try:
        provider = prompt_provider()

        manager = ConfigManager()

        config = manager.load()

        config.llm.provider = provider

        manager.save(config)

        success(f"LLM provider updated to: [bold white]{provider}[/bold white]")

    except KeyboardInterrupt:
        console.print()

        error("Cancelled by user.")


@config_app.command("model")
def model_cmd() -> None:
    """Interactively change the configured LLM model."""

    try:
        manager = ConfigManager()

        config = manager.load()

        provider = config.llm.provider

        if not provider:
            warning(
                "No provider is currently configured. Please select a provider first."
            )

            provider = prompt_provider()

            config.llm.provider = provider

        model = prompt_model(provider)

        config.llm.model = model

        manager.save(config)

        success(f"LLM model updated to: [bold white]{model}[/bold white]")

    except KeyboardInterrupt:
        console.print()

        error("Cancelled by user.")


@config_app.command("key")
def key_cmd() -> None:
    """Update the API key for the configured provider."""

    try:
        manager = ConfigManager()

        config = manager.load()

        provider = config.llm.provider

        if not provider:
            warning(
                "No provider is currently configured. Please select a provider first."
            )

            provider = prompt_provider()

            config.llm.provider = provider

            manager.save(config)

        metadata = PROVIDERS.get(provider.lower())

        if metadata and not metadata.requires_api_key:
            info(f"Provider '{provider}' does not require an API key.")

            return

        api_key = prompt_api_key(provider)

        if api_key is not None:
            env_manager = EnvironmentManager()

            env_manager.set_api_key(provider, api_key)

            success(
                f"API key updated successfully for provider: [bold white]{provider}[/bold white]"
            )

    except KeyboardInterrupt:
        console.print()

        error("Cancelled by user.")


@config_app.command("reset")
def reset_cmd() -> None:
    """Reset configuration and optionally clear stored API keys."""

    try:
        if confirm("Are you sure you want to restore the default configuration?"):
            manager = ConfigManager()

            manager.reset()

            if confirm("Do you also want to remove all stored API keys?"):
                env_manager = EnvironmentManager()

                env_manager.create()

                success(
                    "Configuration and stored API keys have been reset to defaults."
                )

            else:
                success(
                    "Configuration has been reset to defaults. Stored API keys were kept."
                )

    except KeyboardInterrupt:
        console.print()

        error("Cancelled by user.")
