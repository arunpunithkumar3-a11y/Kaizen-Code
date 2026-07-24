from kaizen.config.constants import CONFIG_FILE, ENV_FILE
from kaizen.config.manager import ConfigManager
from kaizen.config.validator import ConfigValidator
from rich import box
from rich.panel import Panel
from rich.table import Table

from kaizen.cli.ui.console import console


def doctor() -> None:
    """Run diagnostics to verify Kaizen Code health."""

    results = []

    config_exists = CONFIG_FILE.exists()

    results.append(
        (
            "Configuration file exists",
            "[#00ff87]✔ Passed[/#00ff87]"
            if config_exists
            else "[#ff5f87]✘ Failed[/#ff5f87]",
            f"Path: {CONFIG_FILE}"
            if config_exists
            else "Config file is missing. Run 'kaizen init' to configure.",
        )
    )

    env_exists = ENV_FILE.exists()

    results.append(
        (
            "Environment file (.env) exists",
            "[#00ff87]✔ Passed[/#00ff87]"
            if env_exists
            else "[#ff5f87]✘ Failed[/#ff5f87]",
            f"Path: {ENV_FILE}"
            if env_exists
            else "Environment file is missing. Run 'kaizen init' to configure.",
        )
    )

    config = None

    if config_exists:
        try:
            manager = ConfigManager()

            config = manager.load()

            results.append(
                (
                    "Configuration loaded successfully",
                    "[#00ff87]✔ Passed[/#00ff87]",
                    f"Provider: {config.llm.provider or 'Not set'}, Model: {config.llm.model or 'Not set'}",
                )
            )

        except Exception as e:
            results.append(
                (
                    "Configuration loaded successfully",
                    "[#ff5f87]✘ Failed[/#ff5f87]",
                    f"Error loading configuration: {e}",
                )
            )

    else:
        results.append(
            (
                "Configuration loaded successfully",
                "[#ffaf5f]⚠ Skipped[/#ffaf5f]",
                "Skipped because config file does not exist.",
            )
        )

    if config is not None:
        try:
            validator = ConfigValidator()

            validator.validate(config)

            results.append(
                (
                    "Configuration validation",
                    "[#00ff87]✔ Passed[/#00ff87]",
                    "All configuration parameters and API keys are valid.",
                )
            )

        except Exception as e:
            results.append(
                (
                    "Configuration validation",
                    "[#ff5f87]✘ Failed[/#ff5f87]",
                    f"Validation failed: {e}",
                )
            )

    else:
        results.append(
            (
                "Configuration validation",
                "[#ffaf5f]⚠ Skipped[/#ffaf5f]",
                "Skipped because configuration could not be loaded.",
            )
        )

    table = Table(box=box.SIMPLE, header_style="bold #875fdf")

    table.add_column("Diagnostic Check")

    table.add_column("Result")

    table.add_column("Details")

    all_passed = True

    for check, res, details in results:
        table.add_row(check, res, details)

        if "✘ Failed" in res:
            all_passed = False

    if all_passed:
        title = "[bold #00ff87]🩺 Kaizen Code Diagnostic Summary - All Passed[/bold #00ff87]"

        border_style = "#00ff87"

    else:
        title = "[bold #ff5f87]🩺 Kaizen Code Diagnostic Summary - Issues Found[/bold #ff5f87]"

        border_style = "#ff5f87"

    panel = Panel(
        table,
        title=title,
        border_style=border_style,
        box=box.ROUNDED,
        expand=False,
        padding=(1, 2),
    )

    console.print(panel)
