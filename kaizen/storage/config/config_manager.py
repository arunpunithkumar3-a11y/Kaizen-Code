import json

from kaizen.storage.paths import CONFIG_DIR


class ConfigManager:
    def __init__(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        self.config_file = CONFIG_DIR / "settings.json"
        if not self.config_file.exists():
            self.config_file.write_text(
                json.dumps(
                    {
                        "config": {
                            "KAIZEN_MODEL": "",
                            "KAIZEN_BASE_URL": "",
                            "KAIZEN_API_KEY": "",
                        }
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _load_config(self) -> dict:
        return json.loads(self.config_file.read_text(encoding="utf-8"))

    def config(self, data: dict) -> None:
        existing_data = self._load_config()
        existing_data["config"] = data
        self.config_file.write_text(
            json.dumps(existing_data, indent=2), encoding="utf-8"
        )

    def show_config(self) -> dict:
        return self._load_config()


config_service = ConfigManager()
