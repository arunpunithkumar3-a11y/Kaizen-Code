import uuid
import json
from pathlib import Path
from datetime import datetime, UTC
from paths import SESSIONS_DIR

class SessionManager:
    def __init__(self):
        SESSIONS_DIR.mkdir(exist_ok=True)
        self.index_file = SESSIONS_DIR / "index.json"
        if not self.index_file.exists():
            self.index_file.write_text(
                json.dumps({"sessions": {}}, indent=2),
                encoding="utf-8"
            )

    def _load_index(self) -> dict:
        return json.loads(self.index_file.read_text(encoding="utf-8"))

    def _save_index(self, data: dict) -> None:
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def session_exists(self, thread_id: str) -> bool:
        data = self._load_index()
        return thread_id in data.get("sessions", {})

    def create(self, title: str) -> str:
        thread_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()

        index_data = self._load_index()
        index_data["sessions"][thread_id] = {
            "title": title,
            "created_at": now
        }
        self._save_index(index_data)

        return thread_id

    def get_session(self, thread_id: str) -> dict:
        if not self.session_exists(thread_id):
            return {}
        data = self._load_index()
        return data["sessions"].get(thread_id, {})

    def list_sessions(self) -> dict:
        data = self._load_index()
        return data.get("sessions", {})

    def delete_session(self, thread_id: str) -> bool:
        if not self.session_exists(thread_id):
            return False

        index_data = self._load_index()
        del index_data["sessions"][thread_id]
        self._save_index(index_data)

        return True
