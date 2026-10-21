"""
TUI Interface for Router Automation & Reboot
"""
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.theme import console
from core.utils import clear_screen, pause
from .manager import RouterManager
from .presets import ROUTER_PRESETS


def render_router_dashboard(manager: RouterManager, probe_info: dict) -> None:
    """Renders the router summary and current status table."""
    status_str = "[bold green]ONLINE (Port 80 Terbuka)[/bold green]" if probe_info.get("is_reachable") else "[bold red]OFFLINE / Tidak Terjangkau[/bold red]"

    table = Table(title="[bold white]📡 ROUTER NETWORK DOSSIER[/bold white]", border_style="red", expand=True)
    table.add_column("Parameter", style="bold red", width=22)
    table.add_column("Detail / Status", style="bold white")

    table.add_row("Target Gateway IP", f"[bold white on red] {manager.host} [/bold white on red]")
    table.add_row("Status Web Portal", status_str)
    table.add_row("Server Signature", probe_info.get("server", "Unknown"))
    table.add_row("Model Terdeteksi", probe_info.get("title", "Generic Router"))
    table.add_row("Driver Aktif", manager.current_preset.get("driver", "zte").upper())
    table.add_row("Username Aktif", f"[bold cyan]{manager.username}[/bold cyan]")
    table.add_row("Password Aktif", f"[bold yellow]{manager.password or '(kosong)'}[/bold yellow]")
    table.add_row("Profil / ISP", manager.current_preset.get("isp", "Custom"))

    console.print(table)


def render_presets_table() -> None:
    """Renders table of default router credentials."""
    table = Table(
        title="[bold white]📋 DAFTAR KREDENSIAL DEFAULT ROUTER INDONESIA[/bold white]",
        border_style="dim red",
        expand=True
    )
    table.add_column("No", style="bold red", width=4, justify="center")
    table.add_column("Profil / ISP", style="bold white", width=26)
    table.add_column("Username", style="cyan", width=14)
    table.add_column("Password", style="yellow", width=16)
    table.add_column("Model / Deskripsi", style="dim white")

    for idx, p in enumerate(ROUTER_PRESETS, start=1):
        table.add_row(
            str(idx),
            p["isp"],
            p["username"],
            p["password"] or "(kosong)",
            f"{p['model']} - {p['description']}"
        )
    console.print(table)


def run_router_module() -> None:
    """Main interactive runner for Router Automation module."""
    manager = RouterManager()

    while True:
        clear_screen()
        header = Panel(
            "[bold red]AKATSUKI ROUTER AUTOMATION & REBOOT[/bold red]\n"
            "[white]Automasi reboot dan manajemen router WiFi lokal tanpa harus buka browser.[/white]\n"
            "[dim white]Mendukung ZTE F609/F670L (IndiHome), Huawei HG8245, TP-Link & generic router.[/dim white]",
            border_style="red",
            title="[bold white]MODUL 2[/bold white]"
        )
        console.print(header)

        with console.status("[bold red]Memeriksa status gateway router lokal...[/bold red]", spinner="dots"):
            probe_info = manager.probe_router()

        console.print()
        render_router_dashboard(manager, probe_info)
        console.print()

        # Action Menu
        menu_table = Table(show_header=False, border_style="red", expand=True, box=None)
        menu_table.add_column("Key", style="bold red", width=6, justify="center")
        menu_table.add_column("Aksi", style="bold white")

        menu_table.add_row("[1]", "⚡ [bold red]REBOOT ROUTER SEKARANG[/bold red] (Kirim sinyal restart)")
        menu_table.add_row("[2]", "🔍 Test Login / Validasi Kredensial")
        menu_table.add_row("[3]", "📋 Lihat & Pilih Kredensial Default (ZTE / Huawei / TP-Link)")
        menu_table.add_row("[4]", "✏️  Input Kredensial Manual (Custom Username / Password)")
        menu_table.add_row("[5]", f"🌐 Ubah IP Gateway Target (Saat ini: {manager.host})")
        menu_table.add_row("[0]", "🚪 Kembali ke Menu Utama")

        console.print(Panel(menu_table, title="[bold white]MENU TINDAKAN ROUTER[/bold white]", border_style="red"))

        try:
            choice = input("\n[Router Action] > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break

        elif choice == "1":
            # Reboot router
            console.print(f"\n[bold yellow]Mengirim sinyal reboot ke {manager.host} dengan akun '{manager.username}'...[/bold yellow]")
            with console.status("[bold red]Mengirim instruksi restart ke router...[/bold red]", spinner="bouncingBar"):
                success, msg = manager.execute_reboot()
            if success:
                console.print(Panel(
                    f"[bold green]✔ BERHASIL![/bold green]\n{msg}\n"
                    f"[white]Router sedang melakukan proses booting ulang (~1-2 menit).[/white]\n"
                    f"[dim white]Koneksi WiFi Anda akan terputus sesaat dan tersambung kembali.[/dim white]",
                    border_style="green",
                    title="[bold white]STATUS REBOOT[/bold white]"
                ))
            else:
                console.print(Panel(
                    f"[bold red]✖ GAGAL MEREBOOT![/bold red]\n{msg}\n"
                    f"[dim white]Cobalah opsi [3] untuk memilih profil username/password lain atau [2] untuk test login.[/dim white]",
                    border_style="red",
                    title="[bold white]STATUS REBOOT[/bold white]"
                ))
            pause()

        elif choice == "2":
            # Test Login
            console.print(f"\n[bold white]Menguji autentikasi ke http://{manager.host} sebagai '{manager.username}'...[/bold white]")
            with console.status("[bold red]Menguji login router...[/bold red]", spinner="dots"):
                ok, msg = manager.test_login()
            if ok:
                console.print(f"\n[bold green]✔ {msg}[/bold green]")
            else:
                console.print(f"\n[bold red]✖ {msg}[/bold red]")
            pause()

        elif choice == "3":
            # Select preset credentials
            clear_screen()
            render_presets_table()
            console.print("\n[bold white]Pilih nomor profil router untuk digunakan (1 - %d):[/bold white]" % len(ROUTER_PRESETS))
            p_choice = input("[Nomor Profil] > ").strip()
            if p_choice.isdigit():
                idx = int(p_choice) - 1
                if 0 <= idx < len(ROUTER_PRESETS):
                    manager.current_preset = ROUTER_PRESETS[idx]
                    manager.username = ROUTER_PRESETS[idx]["username"]
                    manager.password = ROUTER_PRESETS[idx]["password"]
                    console.print(f"\n[bold green]✔ Profil aktif diubah ke: {ROUTER_PRESETS[idx]['isp']} ({manager.username} / {manager.password})[/bold green]")
                    pause()

        elif choice == "4":
            # Manual credentials
            console.print("\n[bold white]Masukkan Username baru:[/bold white]")
            new_user = input("[Username] > ").strip()
            console.print("[bold white]Masukkan Password baru:[/bold white]")
            new_pass = input("[Password] > ").strip()
            if new_user:
                manager.username = new_user
                manager.password = new_pass
                manager.current_preset = {
                    "isp": "Custom User Config",
                    "model": "Custom",
                    "username": new_user,
                    "password": new_pass,
                    "driver": manager.current_preset.get("driver", "zte"),
                    "description": "Kredensial kustom pengguna"
                }
                console.print(f"\n[bold green]✔ Kredensial aktif diubah ke: {new_user}[/bold green]")
                pause()

        elif choice == "5":
            # Change Gateway IP
            console.print(f"\n[bold white]Masukkan IP Gateway target (Default: 192.168.1.1 atau 192.168.100.1):[/bold white]")
            new_ip = input("[IP Router] > ").strip()
            if new_ip:
                manager.host = new_ip
                console.print(f"\n[bold green]✔ Target router diubah ke: {new_ip}[/bold green]")
                pause()
