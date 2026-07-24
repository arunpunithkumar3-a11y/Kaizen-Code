from questionary import Style
from rich.theme import Theme

KAIZEN_THEME = Theme(
    {
        "banner": "bold #875fdf",
        "brand": "bold #875fdf",
        "accent": "bold #00d7ff",
        "success": "#00ff87",
        "success_bold": "bold #00ff87",
        "error": "#ff5f87",
        "error_bold": "bold #ff5f87",
        "warning": "#ffaf5f",
        "warning_bold": "bold #ffaf5f",
        "info": "#5f87ff",
        "info_bold": "bold #5f87ff",
        "muted": "#8a8a8a",
        "muted_bold": "bold #8a8a8a",
    }
)


QUESTIONARY_STYLE = Style(
    [
        ("qmark", "fg:#875fdf bold"),
        ("question", "bold fg:#ffffff"),
        ("answer", "fg:#00ff87 bold"),
        ("pointer", "fg:#00d7ff bold"),
        ("highlighted", "fg:#00d7ff bold"),
        ("selected", "fg:#00ff87 bold"),
        ("separator", "fg:#8a8a8a"),
        ("instruction", "fg:#8a8a8a italic"),
        ("text", "fg:#ffffff"),
        ("disabled", "fg:#5f5f5f italic"),
    ]
)
