import questionary
from kaizen.config.constants import PROVIDERS

from kaizen.cli.ui.styles import QUESTIONARY_STYLE


def prompt_provider() -> str:

    provider = questionary.select(
        "🤖 Select your LLM provider:",
        choices=list(PROVIDERS.keys()),
        style=QUESTIONARY_STYLE,
    ).ask()

    if provider is None:
        raise KeyboardInterrupt()

    return provider


def prompt_model(provider: str) -> str:

    model = questionary.text(
        f"⚙️ Enter LLM model for {provider}:",
        style=QUESTIONARY_STYLE,
    ).ask()

    if model is None:
        raise KeyboardInterrupt()

    return model.strip()


def prompt_api_key(provider: str) -> str | None:

    provider_metadata = PROVIDERS[provider]

    if not provider_metadata.requires_api_key:
        return None

    api_key = questionary.password(
        f"🔑 Enter your {provider} API key:",
        style=QUESTIONARY_STYLE,
    ).ask()

    if api_key is None:
        raise KeyboardInterrupt()

    return api_key.strip()


def confirm(message: str) -> bool:

    result = questionary.confirm(
        f"❓ {message}",
        style=QUESTIONARY_STYLE,
    ).ask()

    if result is None:
        raise KeyboardInterrupt()

    return result
