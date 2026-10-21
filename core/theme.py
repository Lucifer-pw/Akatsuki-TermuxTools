"""
Akatsuki Theme Definitions for Rich Console
"""
import sys

# Ensure UTF-8 output encoding across Windows and Termux
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.theme import Theme
from rich.console import Console
from rich.style import Style

# Color Palette
COLOR_RED = "#ff1744"          # Akatsuki Crimson Cloud
COLOR_DARK_RED = "#b71c1c"     # Shadow / Deep Crimson
COLOR_WHITE = "#ffffff"        # Outer Cloud Outline / Main Text
COLOR_GRAY = "#9e9e9e"         # Metadata / Secondary Text
COLOR_DARK_GRAY = "#424242"    # Subtle borders
COLOR_BLACK = "#121212"        # Pitch Black Background

akatsuki_theme = Theme({
    "red": COLOR_RED,
    "dark_red": COLOR_DARK_RED,
    "white": COLOR_WHITE,
    "gray": COLOR_GRAY,
    "grey": COLOR_GRAY,
    "title": f"bold {COLOR_RED}",
    "subtitle": f"bold {COLOR_WHITE}",
    "border": COLOR_RED,
    "dim_border": COLOR_DARK_GRAY,
    "success": "bold green",
    "warning": "bold yellow",
    "error": f"bold {COLOR_RED}",
    "info": "bold cyan",
    "key": f"bold {COLOR_WHITE}",
    "value": f"{COLOR_RED}",
    "badge": f"bold {COLOR_WHITE} on {COLOR_DARK_RED}",
})

console = Console(theme=akatsuki_theme)
