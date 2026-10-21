"""
Interactive TUI Menu Component
Designed for Termux with fast number key selection and responsive panels.
"""
from typing import List, Tuple, Optional
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from .theme import console


def display_menu(
    options: List[Tuple[str, str, str]],
    title: str = "MAIN MENU",
    footer_hint: str = "Pilih nomor opsi lalu tekan Enter"
) -> None:
    """
    Renders an options list in a clean Akatsuki-styled table.
    options format: [(key_number, title, description), ...]
    """
    table = Table(
        show_header=True,
        header_style="bold red",
        border_style="red",
        expand=True,
        box=None
    )
    table.add_column("Key", style="bold red", width=6, justify="center")
    table.add_column("Fitur / Modul", style="bold white", width=26)
    table.add_column("Keterangan", style="dim white")

    for key, opt_title, opt_desc in options:
        if key == "0":
            table.add_row(f"[bold white on red] {key} [/bold white on red]", f"[bold white]{opt_title}[/bold white]", f"[dim]{opt_desc}[/dim]")
        else:
            table.add_row(f"[bold red][{key}][/bold red]", f"[bold white]{opt_title}[/bold white]", opt_desc)

    panel = Panel(
        table,
        title=f"[bold white]{title}[/bold white]",
        border_style="red",
        subtitle=f"[dim white]{footer_hint}[/dim white]",
        subtitle_align="center"
    )
    console.print(panel)


def prompt_choice(prompt_text: str = "akatsuki@termux:~$ ") -> str:
    """
    Displays an Akatsuki prompt and captures user input.
    """
    console.print(f"[bold red]»»[/bold red] [bold white]{prompt_text}[/bold white]", end="")
    try:
        choice = input().strip()
        return choice
    except (KeyboardInterrupt, EOFError):
        return "0"
