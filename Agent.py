import questionary
from questionary import Choice

from kaizen.storage.db.session_manager import session_service


def resume():
    data = [
        Choice(y["title"], value=x) for x, y in session_service.list_sessions().items()
    ]
    thread_id = questionary.select("Choose Chats", choices=data).ask()
    print(thread_id)


resume()
