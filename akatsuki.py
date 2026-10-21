#!/usr/bin/env python3
"""
AKATSUKI TERMUX TOOLS SUITE v2.0
Modern TUI Utility Suite with Akatsuki Theme (Red & Black Aesthetic)
Recreated for Android Termux and modern cross-platform environments.
"""
import sys
import os

# Ensure project root is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.theme import console
from core.banner import render_banner
from core.menu import display_menu, prompt_choice
from core.utils import (
    get_system_summary,
    clear_screen,
    pause,
    load_config,
    save_config,
    is_termux
)

# Feature Modules
from modules.osint_phone import run_osint_phone_module
from modules.router_control import run_router_module
from modules.net_optimizer import run_network_module
from modules.net_security import run_net_security_module
import subprocess

from rich.panel import Panel
from rich.table import Table


def show_about_screen() -> None:
    """Displays information and credits about Akatsuki Termux Tools."""
    clear_screen()
    content = (
        "[bold red]AKATSUKI TERMUX TOOLS v2.0[/bold red]\n"
        "[white]Recreated from the classic 2020 Termux tool suite with a modern TUI architecture.[/white]\n\n"
        "[bold white]Fitur Utama:[/bold white]\n"
        "  • [bold red]OSINT Phone Scanner:[/bold red] Format E.164, operator seluler, timezone, & search dorks.\n"
        "  • [bold red]Router Automation:[/bold red] Reboot router lokal (ZTE, Huawei, TP-Link) langsung via CLI.\n"
        "  • [bold red]Network Optimizer:[/bold red] DNS benchmark, ping keep-alive anti WiFi sleep, MTU finder.\n"
        "  • [bold red]Akatsuki TUI Engine:[/bold red] Rich console layout dengan tema awan merah Akatsuki.\n\n"
        "[dim white]Lingkungan Saat Ini:[/dim white] [bold white]"
        + ("Termux (Android)" if is_termux() else sys.platform)
        + "[/bold white]\n"
        "[dim white]Author / Maintainer:[/dim white] [bold red]Akatsuki Syndicate / Reborn 2026[/bold red]"
    )
    console.print(Panel(content, title="[bold white]TENTANG TOOLS[/bold white]", border_style="red"))
    pause()


def show_settings_screen() -> None:
    """Displays and modifies basic configuration settings."""
    while True:
        clear_screen()
        cfg = load_config()
        r_cfg = cfg.get("router", {})
        o_cfg = cfg.get("osint", {})

        table = Table(title="[bold white]⚙️  KONFIGURASI SISTEM[/bold white]", border_style="red", expand=True)
        table.add_column("Key", style="bold red", width=6, justify="center")
        table.add_column("Parameter", style="bold white", width=26)
        table.add_column("Nilai Saat Ini", style="cyan")

        table.add_row("[1]", "Default Gateway IP", r_cfg.get("gateway_ip", "auto"))
        table.add_row("[2]", "Default Router Username", r_cfg.get("username", "user"))
        table.add_row("[3]", "Default Router Password", r_cfg.get("password", "user1234"))
        table.add_row("[4]", "Default OSINT Region", o_cfg.get("default_region", "ID"))
        table.add_row("[0]", "Kembali ke Menu Utama", "[dim]Simpan & keluar[/dim]")

        console.print(Panel(table, border_style="red"))

        try:
            choice = input("\n[Setting Item (0 to Back)] > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break
        elif choice == "1":
            new_gw = input("Masukkan Gateway IP baru (atau 'auto'): ").strip()
            if new_gw:
                r_cfg["gateway_ip"] = new_gw
                cfg["router"] = r_cfg
                save_config(cfg)
        elif choice == "2":
            new_u = input("Masukkan Username router default baru: ").strip()
            if new_u:
                r_cfg["username"] = new_u
                cfg["router"] = r_cfg
                save_config(cfg)
        elif choice == "3":
            new_p = input("Masukkan Password router default baru: ").strip()
            if new_p:
                r_cfg["password"] = new_p
                cfg["router"] = r_cfg
                save_config(cfg)
        elif choice == "4":
            new_reg = input("Masukkan Region Code default (e.g. ID, US, SG): ").strip().upper()
            if new_reg:
                o_cfg["default_region"] = new_reg
                cfg["osint"] = o_cfg
                save_config(cfg)


def update_akatsuki_tools() -> None:
    """Pulls latest updates from GitHub."""
    clear_screen()
    console.print(Panel(
        "[bold red]✦ AUTO-UPDATE AKATSUKI TOOLS[/bold red]\n"
        "[white]Mengambil pembaruan fitur terbaru langsung dari repositori GitHub...[/white]",
        border_style="red"
    ))
    with console.status("[bold red]Menjalankan git pull origin main...[/bold red]", spinner="dots"):
        try:
            proc = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, timeout=25)
            if proc.returncode == 0:
                console.print(f"\n[bold green]✔ BERHASIL DI-UPDATE![/bold green]\n[dim white]{proc.stdout.strip()}[/dim white]")
                console.print("\n[bold white]Pembaruan selesai! Silakan jalankan ulang aplikasi untuk memuat kode terbaru.[/bold white]")
            else:
                console.print(f"\n[bold yellow]▲ Hasil git pull:[/bold yellow]\n{proc.stdout or proc.stderr}")
        except Exception as e:
            console.print(f"\n[bold red]✖ Gagal update:[/bold red] {e}")
    pause()


def main():
    """Main application loop."""
    menu_options = [
        ("1", "📱 OSINT Phone Intelligence", "Validasi format E.164, operator, & generator search dorks publik"),
        ("2", "📡 Router Automation (Reboot)", "Otomatisasi restart router WiFi lokal & deteksi kredensial default"),
        ("3", "⚡ Network & Bandwidth Optimizer", "Benchmark Multi-DNS tercepat, ping keep-alive, & MTU analyzer"),
        ("4", "🛡️ Network Security & Protection", "Anti-NetCut Sentinel, deteksi penyusup WiFi, & audit Nmap"),
        ("5", "🔄 Update Akatsuki Tools", "Tarik update kodingan terbaru langsung dari GitHub (Git Pull)"),
        ("6", "⚙️  Pengaturan & Konfigurasi", "Kelola preferensi gateway, kredensial, & default region"),
        ("7", "ℹ️  Tentang Akatsuki Tools", "Informasi versi, arsitektur, & kredit"),
        ("0", "Keluar dari Akatsuki", "Tutup session terminal")
    ]

    while True:
        try:
            clear_screen()
            summary = get_system_summary()
            console.print(render_banner(summary))
            console.print()
            display_menu(menu_options, title="AKATSUKI DASHBOARD - MAIN MENU")
            
            choice = prompt_choice("Pilih nomor menu [0-7]: ")

            if choice == "0":
                clear_screen()
                console.print(Panel(
                    "[bold red]»»[/bold red] [bold white]Terima kasih telah menggunakan Akatsuki Termux Tools. Sampai jumpa di balik bayangan.[/bold white]",
                    border_style="red"
                ))
                break

            elif choice == "1":
                run_osint_phone_module()

            elif choice == "2":
                run_router_module()

            elif choice == "3":
                run_network_module()

            elif choice == "4":
                run_net_security_module()

            elif choice == "5":
                update_akatsuki_tools()

            elif choice == "6":
                show_settings_screen()

            elif choice == "7":
                show_about_screen()

            else:
                console.print("\n[bold red]Pilihan tidak valid! Masukkan angka antara 0 sampai 7.[/bold red]")
                pause()

        except KeyboardInterrupt:
            clear_screen()
            console.print("\n[bold red]Session dihentikan oleh pengguna (Ctrl+C).[/bold red]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Terjadi kesalahan tidak terduga:[/bold red] {e}")
            pause()


if __name__ == "__main__":
    main()
