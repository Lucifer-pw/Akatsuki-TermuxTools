"""
Akatsuki Cloud ASCII Art & Header Banner Generator
Engineered specifically for mobile Termux screens:
- Pure ASCII curves and contours matching the iconic Akatsuki Red Cloud
- Compact width (38 columns) so it NEVER wraps on smartphone screens
- Vivid Crimson Red and Crisp White styling
"""
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from .theme import console, COLOR_RED, COLOR_WHITE, COLOR_GRAY, COLOR_DARK_RED
import shutil

# Iconic Akatsuki Cloud silhouette with white border and red core
AKATSUKI_CLOUD = r"""[bold white]
               _..----.._
            .-'          '-.
          .'   [bold red]_..----.._ [/bold red]  '.
  _     .'   [bold red].'   ___    '. [/bold red]  '.
 / \   /    [bold red]/   .'   '.    \ [/bold red]   \
|   \_:    [bold red]:   /   ()  \    : [/bold red]   :
 \        [bold red]:   :    __   :    : [/bold red]   :
  '-.__   [bold red] \   \  (__) /    / [/bold red]   /
       '-. [bold red] '._ '----' _.-' [/bold red] .-'
          '-.._ [bold red]'----' [/bold red]_..--'
               '------'[/bold white]
[bold red]      === A K A T S U K I ===[/bold red]
[dim white]  'Know pain, know peace. Suite v2.0'[/dim white]"""


def render_banner(system_info: dict = None) -> Panel:
    """
    Renders the Akatsuki header banner inside a styled Rich Panel.
    Always displays the iconic red cloud logo.
    """
    if system_info:
        gateway = system_info.get("gateway", "Unknown")
        local_ip = system_info.get("local_ip", "127.0.0.1")
        battery = system_info.get("battery", "N/A")
        net_type = system_info.get("net_type", "WiFi")
        
        status_line = (
            f"\n[dim white]IP:[/dim white] [bold white]{local_ip}[/bold white]  "
            f"[dim white]|[/dim white]  [dim white]GW:[/dim white] [bold red]{gateway}[/bold red]  "
            f"[dim white]|[/dim white]  [dim white]Net:[/dim white] [bold white]{net_type}[/bold white]  "
            f"[dim white]|[/dim white]  [dim white]Batt:[/dim white] [bold green]{battery}[/bold green]"
        )
    else:
        status_line = "\n[dim white]Akatsuki terminal active. Ready for operations.[/dim white]"

    full_content = f"{AKATSUKI_CLOUD}\n{status_line}"

    banner_panel = Panel(
        Align.center(full_content),
        border_style="red",
        padding=(0, 1),
        title="[bold white]AKATSUKI TERMINAL[/bold white]",
        title_align="center",
        subtitle="[dim red]Shadow Cloud Suite[/dim red]",
        subtitle_align="right"
    )
    return banner_panel


if __name__ == "__main__":
    console.print(render_banner({"gateway": "192.168.1.1", "local_ip": "192.168.1.15", "battery": "88%", "net_type": "WiFi"}))
