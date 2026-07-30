from pathlib import Path

from kaizen.storage.paths import (
    CONFIG_DIR,
    KAIZEN_HOME,
    SESSIONS_DIR,
)


class StorageManager:
    """Initializes and manages Kaizen's local storage"""

    DIRECTORIES: tuple[Path, ...] = (KAIZEN_HOME, CONFIG_DIR, SESSIONS_DIR)

    @classmethod
    def initialize(cls) -> None:
        """Create the required directory structure if it doesnt exist."""
        for dir in cls.DIRECTORIES:
            dir.mkdir(parents=True, exist_ok=True)


storage_manager = StorageManager()
