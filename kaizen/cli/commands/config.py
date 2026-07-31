from kaizen.cli.ui.console import console
from kaizen.storage.config.config_manager import config_service


def config():
    import questionary
    from kaizen.cli.ui import panels
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE

    current_config = config_service.show_config().get("config", {})
    default_url = current_config.get("KAIZEN_BASE_URL", "")
    default_model = current_config.get("KAIZEN_MODEL", "")
    default_api_key = current_config.get("KAIZEN_API_KEY", "")

    panels.show_banner()
    console.print("  [dim]Configure LLM settings. Press Enter to keep current values.[/dim]\n")

    base_url = questionary.text(
        "🌐 Base URL:",
        default=default_url,
        style=QUESTIONARY_STYLE,
        qmark="  ❖",
    ).ask()
    if base_url is None:
        return

    model = questionary.text(
        "🤖 Model Name:",
        default=default_model,
        style=QUESTIONARY_STYLE,
        qmark="  ❖",
    ).ask()
    if model is None:
        return

    api_key = questionary.password(
        "🔑 API Key:",
        default=default_api_key,
        style=QUESTIONARY_STYLE,
        qmark="  ❖",
    ).ask()
    if api_key is None:
        return

    data = {
        "KAIZEN_MODEL": model.strip(),
        "KAIZEN_BASE_URL": base_url.strip(),
        "KAIZEN_API_KEY": api_key.strip(),
    }
    config_service.config(data=data)

    console.print()
    panels.success("Configuration updated successfully.")

