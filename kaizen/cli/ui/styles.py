from questionary import Style
from rich.theme import Theme

KAIZEN_THEME = Theme(
    {
        "banner": "bold #7c3aed",
        "brand": "bold #7c3aed",
        "accent": "bold #6366f1",
        "success": "#10b981",
        "success_bold": "bold #10b981",
        "error": "#ef4444",
        "error_bold": "bold #ef4444",
        "warning": "#f59e0b",
        "warning_bold": "bold #f59e0b",
        "info": "#3b82f6",
        "info_bold": "bold #3b82f6",
        "muted": "#6c7086",
        "muted_bold": "bold #6c7086",

        "markdown.h1": "bold #7c3aed",
        "markdown.h2": "bold #6366f1",
        "markdown.h3": "bold #3b82f6",
        "markdown.h4": "bold #b4befe",
        "markdown.code": "bold #6366f1",
        "markdown.block_quote": "italic #6c7086",
        "markdown.item": "white",
        "markdown.link": "underline #3b82f6",
        "markdown.link_text": "underline #3b82f6",
    }
)


QUESTIONARY_STYLE = Style(
    [
        ("qmark", "fg:#7c3aed bold"),
        ("question", "bold fg:#ffffff"),
        ("answer", "fg:#10b981 bold"),
        ("pointer", "fg:#a78bfa bold"),
        ("highlighted", "fg:#ffffff bg:#7c3aed bold"),
        ("selected", "fg:#10b981 bold"),
        ("separator", "fg:#6c7086"),
        ("instruction", "fg:#6c7086 italic"),
        ("text", "fg:#ffffff"),
        ("disabled", "fg:#5f5f5f italic"),
    ]
)
