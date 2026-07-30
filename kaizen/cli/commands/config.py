from rich.console import Console

from kaizen.storage.config.config_manager import config_service

console = Console()


def config():
    KAIZEN_BASE_URL = input("Enter Base Url: ")
    KAIZEN_MODEL = input("Enter the model: ")
    KAIZEN_API_KEY = input("Enter the API key: ")
    data = {
        "KAIZEN_MODEL": KAIZEN_MODEL,
        "KAIZEN_BASE_URL": KAIZEN_BASE_URL,
        "KAIZEN_API_KEY": KAIZEN_API_KEY,
    }
    config_service.config(data=data)
    console.print("[bold #00ff87]success[/bold #00ff87]")
