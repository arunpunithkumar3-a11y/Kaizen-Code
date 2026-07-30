from kaizen.cli.ui import panels
from kaizen.storage.manager import storage_manager


def init():
    panels.show_banner()
    panels.log_action("Planning", "Initializing Kaizen Code storage...")
    storage_manager.initialize()
    panels.success("Initialization complete.")

