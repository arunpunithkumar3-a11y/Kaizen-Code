import sys

from rich.console import Console

from kaizen.cli.ui.styles import KAIZEN_THEME

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")

        sys.stderr.reconfigure(encoding="utf-8")

    except Exception:
        pass


console = Console(theme=KAIZEN_THEME)
