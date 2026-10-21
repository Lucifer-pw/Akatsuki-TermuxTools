"""
TUI Interface for OSINT Phone Intelligence Scanner
"""
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.theme import console
from core.utils import clear_screen, pause
from .parser import parse_phone_number
from .footprint import generate_osint_dorks


def render_phone_summary(meta) -> None:
    """Renders parsed phone intelligence in an Akatsuki-themed table."""
    table = Table(title="[bold white]📱 PHONE INTELLIGENCE DOSSIER[/bold white]", border_style="red", expand=True)
    table.add_column("Parameter", style="bold red", width=22)
    table.add_column("Detail / Value", style="bold white")

    # Status
    if meta.is_valid:
        status_badge = "[bold green]● VALID NUMBER (TERVERIFIKASI)[/bold green]"
    elif meta.is_possible:
        status_badge = "[bold yellow]▲ POSSIBLE FORMAT (BELUM PASTI AKTIF)[/bold yellow]"
    else:
        status_badge = f"[bold red]✖ INVALID NUMBER ({meta.error or 'Format salah'})[/bold red]"

    table.add_row("Status Validasi", status_badge)
    table.add_row("Format E.164", f"[bold white on red] {meta.e164 or '-'} [/bold white on red]")
    table.add_row("Format Internasional", meta.international or "-")
    table.add_row("Format Nasional", meta.national or "-")
    table.add_row("Negara / Teritori", f"{meta.country_name} ([dim]{meta.region_code}[/dim])")
    table.add_row("Kode Negara (CC)", f"+{meta.country_code}")
    table.add_row("Operator / Provider", f"[bold cyan]{meta.carrier or 'Tidak Terdeteksi'}[/bold cyan]")
    table.add_row("Tipe Jaringan", meta.line_type)
    table.add_row("Zona Waktu (TZ)", ", ".join(meta.timezones) if meta.timezones else "-")

    console.print(table)


def render_footprint_table(dorks_dict: dict) -> None:
    """Renders categorized search dorks and profile links."""
    for category, items in dorks_dict.items():
        table = Table(
            title=f"[bold red]✦ {category.upper()}[/bold red]",
            border_style="dim red",
            expand=True,
            show_header=True
        )
        table.add_column("Platform / Target", style="bold white", width=26)
        table.add_column("OSINT Query / Direct Link", style="cyan", overflow="fold")

        for label, url, dork in items:
            table.add_row(label, f"[link={url}]{url}[/link]")

        console.print(table)
        console.print()


def run_osint_phone_module() -> None:
    """Main interactive runner for OSINT Phone module."""
    while True:
        clear_screen()
        header = Panel(
            "[bold red]AKATSUKI OSINT PHONE SCANNER[/bold red]\n"
            "[white]Lacak metadata nomor telepon internasional, operator seluler, dan jejak publik.[/white]\n"
            "[dim white]Mendukung semua format internasional (+62, +1, +44, dsb.) atau nomor lokal.[/dim white]",
            border_style="red",
            title="[bold white]MODUL 1[/bold white]"
        )
        console.print(header)
        console.print("\n[bold white]Masukkan nomor telepon target[/bold white] (contoh: [bold red]+628123456789[/bold red] atau [bold red]+14155552671[/bold red]):")
        console.print("[dim white]Ketik '0' atau 'back' untuk kembali ke menu utama.[/dim white]")
        
        try:
            user_input = input("\n[Phone Target] > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input or user_input in ("0", "back", "exit", "q"):
            break

        # Optional region input if not prefixed with +
        default_reg = "ID"
        if not user_input.startswith("+"):
            console.print("[dim white]Nomor tidak diawali tanda '+'. Gunakan kode negara default (Enter untuk 'ID' / Indonesia, atau ketik kode lain seperti US, SG, MY):[/dim white]")
            reg_input = input("[Region Code (default ID)] > ").strip().upper()
            if reg_input:
                default_reg = reg_input

        with console.status("[bold red]Memproses intelijen nomor...[/bold red]", spinner="dots"):
            meta = parse_phone_number(user_input, default_region=default_reg)
            dorks = generate_osint_dorks(meta)

        console.print("\n")
        render_phone_summary(meta)
        console.print()

        if dorks:
            console.print(Panel(
                "[bold white]Jejak Publik & Link Investigasi Akun Tertaut (OSINT)[/bold white]\n"
                "[dim white]Klik link atau salin URL berikut di browser untuk memeriksa akun sosial & publik:[/dim white]",
                border_style="red"
            ))
            render_footprint_table(dorks)

        pause("Tekan Enter untuk memindai nomor lain...")
