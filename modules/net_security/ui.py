"""
TUI Interface for Network Security & Protection
"""
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.theme import console
from core.utils import clear_screen, pause, get_default_gateway, get_local_ip
from .arp_guard import ARPGuard, run_arp_guard_monitor
from .intruder_alert import check_for_intruders, add_to_whitelist, get_trusted_devices, remove_from_whitelist
from .nmap_scanner import audit_router_security, is_nmap_installed, run_nmap_native_scan, run_python_fallback_scan


def render_intruders_table(res: dict) -> None:
    """Renders table of trusted devices vs detected intruders."""
    console.print(Panel(
        f"[bold white]STATUS JARINGAN WIFI[/bold white]\n"
        f"• Total Terhubung : [bold white]{res['total_connected']}[/bold white] Perangkat\n"
        f"• Terdaftar Aman  : [bold green]{res['trusted_count']}[/bold green] Perangkat\n"
        f"• Penyusup Asing  : [bold red]{res['intruder_count']}[/bold red] Perangkat",
        border_style="red"
    ))

    # 1. Intruders table if any
    if res["intruders"]:
        table = Table(title="[bold red]🚨 PERANGKAT ASING / TIDAK TERDAFTAR (PENYUSUP)[/bold red]", border_style="red", expand=True)
        table.add_column("No", style="bold red", width=4, justify="center")
        table.add_column("IP Address", style="bold white", width=16)
        table.add_column("MAC Address", style="yellow", width=19)
        table.add_column("Merk / Vendor", style="cyan", width=22)
        table.add_column("Status", style="bold white on red", justify="center")

        for idx, dev in enumerate(res["intruders"], start=1):
            table.add_row(
                str(idx),
                dev.get("ip", "-"),
                dev.get("mac", "-"),
                dev.get("vendor", "-"),
                "✖ PENYUSUP ASING"
            )
        console.print(table)
        console.print()

    # 2. Trusted table
    if res["trusted_devices"]:
        table_t = Table(title="[bold green]✔ PERANGKAT TERPERCAYA (WHITELIST)[/bold green]", border_style="green", expand=True)
        table_t.add_column("No", style="bold green", width=4, justify="center")
        table_t.add_column("IP Address", style="bold white", width=16)
        table_t.add_column("MAC Address", style="dim white", width=19)
        table_t.add_column("Merk / Vendor", style="cyan", width=20)
        table_t.add_column("Nama Alias", style="bold white")

        for idx, dev in enumerate(res["trusted_devices"], start=1):
            table_t.add_row(
                str(idx),
                dev.get("ip", "-"),
                dev.get("mac", "-"),
                dev.get("vendor", "-"),
                dev.get("alias", "Perangkat Resmi")
            )
        console.print(table_t)


def render_security_audit(audit: dict) -> None:
    """Renders router security audit findings."""
    console.print(Panel(
        f"[bold white]HASIL AUDIT KEAMANAN ROUTER: {audit['target']}[/bold white]\n"
        f"• Engine Pemindai : [bold cyan]{audit['engine']}[/bold cyan]\n"
        f"• Skor Keamanan   : [bold red]{audit['grade']}[/bold red]\n"
        f"• Vonis Analisis  : [white]{audit['verdict']}[/white]",
        border_style="red"
    ))

    table = Table(title="[bold white]PORT DAN LAYANAN TERBUKA DI ROUTER[/bold white]", border_style="red", expand=True)
    table.add_column("Port", style="bold red", width=8)
    table.add_column("Proto", style="dim white", width=6)
    table.add_column("Layanan", style="bold white", width=16)
    table.add_column("Versi Banner", style="cyan", width=20)
    table.add_column("Level Risiko", style="bold yellow", width=12, justify="center")
    table.add_column("Keterangan Risiko", style="dim white")

    for p in audit["open_services"]:
        lvl = p["risk_level"]
        if lvl == "CRITICAL":
            lvl_style = "[bold white on red] CRITICAL [/bold white on red]"
        elif lvl == "High":
            lvl_style = "[bold red] HIGH [/bold red]"
        elif lvl == "Medium":
            lvl_style = "[bold yellow] MEDIUM [/bold yellow]"
        else:
            lvl_style = "[green] LOW [/green]"

        table.add_row(
            str(p["port"]),
            p["protocol"].upper(),
            p["service"],
            p["version"],
            lvl_style,
            p["description"]
        )

    console.print(table)


def run_net_security_module() -> None:
    """Main interactive runner for Network Security & Protection."""
    gw_ip = get_default_gateway()
    my_ip = get_local_ip()

    while True:
        clear_screen()
        nmap_status = "[bold green]Nmap Asli Aktif[/bold green]" if is_nmap_installed() else "[yellow]Python Fallback Scanner[/yellow]"

        header = Panel(
            "[bold red]AKATSUKI NETWORK SECURITY & PROTECTION[/bold red]\n"
            "[white]Pertahanan anti-NetCut, deteksi penyusup WiFi, dan audit celah keamanan jaringan.[/white]\n"
            f"[dim white]Router: [bold red]{gw_ip}[/bold red] | Host: [bold white]{my_ip}[/bold white] | Engine: {nmap_status}[/dim white]",
            border_style="red",
            title="[bold white]MODUL 4 - SECURITY SENTINEL[/bold white]"
        )
        console.print(header)

        menu_table = Table(show_header=False, border_style="red", expand=True, box=None)
        menu_table.add_column("Key", style="bold red", width=6, justify="center")
        menu_table.add_column("Fitur Keamanan", style="bold white")

        menu_table.add_row("[1]", "🛡️  [bold white]Anti-NetCut Live Sentinel[/bold white] (Deteksi Serangan ARP Spoofing)")
        menu_table.add_row("[2]", "🔒 [bold white]Kunci Gateway Permanen[/bold white] (Static ARP Lock - Kebal NetCut)")
        menu_table.add_row("[3]", "🚨 [bold white]Deteksi Penyusup WiFi Baru[/bold white] (Pindai Perangkat Asing & Whitelist)")
        menu_table.add_row("[4]", "🔍 [bold white]Audit Celah Keamanan Router[/bold white] (Cek Port Berbahaya di 192.168.1.1)")
        menu_table.add_row("[5]", "🎯 [bold white]Port Scanner Custom (Nmap)[/bold white] (Pindai Port Spesifik Perangkat Lain)")
        menu_table.add_row("[0]", "🚪 Kembali ke Menu Utama")

        console.print(Panel(menu_table, title="[bold white]OPSI PERTAHANAN JARINGAN[/bold white]", border_style="red"))

        try:
            choice = input("\n[Security Action] > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break

        elif choice == "1":
            # Anti-NetCut Live Sentinel
            clear_screen()
            run_arp_guard_monitor(interval_sec=2.0)
            pause()

        elif choice == "2":
            # Static ARP Lock
            console.print(f"\n[bold white]Mengunci IP {gw_ip} dengan MAC aslinya secara statis agar kebal dari NetCut...[/bold white]")
            guard = ARPGuard(gw_ip)
            ok, msg = guard.lock_static_arp()
            if ok:
                console.print(f"\n[bold green]✔ {msg}[/bold green]")
            else:
                console.print(f"\n[bold yellow]▲ {msg}[/bold yellow]")
                console.print("[dim white]Tips: Pada Windows jalankan terminal sebagai Administrator. Pada Android Termux memerlukan izin root.[/dim white]")
            pause()

        elif choice == "3":
            # Intruder alert & Whitelist manager
            clear_screen()
            console.print("[bold red]Memindai jaringan dan mencocokkan dengan daftar Whitelist...[/bold red]")
            with console.status("[bold red]Memeriksa perangkat terdaftar...[/bold red]", spinner="dots"):
                res = check_for_intruders()

            console.print()
            render_intruders_table(res)

            console.print("\n[bold white]Tindakan Whitelist:[/bold white]")
            console.print("[dim white]Ketik '[bold red]A[/bold red]' untuk Daftarkan Perangkat ke Whitelist | Ketik '[bold red]Enter[/bold red]' untuk Kembali[/dim white]")
            sub_c = input("[Pilihan] > ").strip().upper()
            if sub_c == "A":
                mac_in = input("Masukkan MAC Address perangkat (contoh: 04:42:1a:e0:f7:93): ").strip()
                name_in = input("Beri nama alias (contoh: HP Ayah / Laptop Adik): ").strip()
                if mac_in and name_in:
                    add_to_whitelist(mac_in, name_in)
                    console.print(f"\n[bold green]✔ Berhasil mendaftarkan {name_in} ({mac_in}) ke Whitelist Aman![/bold green]")
                    pause()

        elif choice == "4":
            # Audit Router
            console.print(f"\n[bold white]Menjalankan audit celah keamanan pada Router {gw_ip}...[/bold white]")
            with console.status("[bold red]Memindai port-port manajemen dan celah router...[/bold red]", spinner="bouncingBar"):
                audit_res = audit_router_security(gw_ip)

            console.print()
            render_security_audit(audit_res)
            pause()

        elif choice == "5":
            # Custom IP Scan
            console.print(f"\n[bold white]Masukkan IP target yang ingin dipindai (Default: {gw_ip}):[/bold white]")
            target_ip = input("[Target IP] > ").strip() or gw_ip
            console.print("[bold white]Masukkan port yang ingin dipindai (Enter untuk port standar 21-8080):[/bold white]")
            port_input = input("[Ports (contoh: 21,22,80,443)] > ").strip()

            if not port_input:
                ports_list = [21, 22, 23, 53, 80, 135, 139, 443, 445, 1900, 3389, 5228, 8080, 8443, 49152]
            else:
                ports_list = [int(p.strip()) for p in port_input.split(",") if p.strip().isdigit()]

            with console.status(f"[bold red]Memindai port pada {target_ip}...[/bold red]", spinner="dots"):
                if is_nmap_installed() and port_input:
                    scan_results = run_nmap_native_scan(target_ip, port_input)
                    if not scan_results:
                        scan_results = run_python_fallback_scan(target_ip, ports_list)
                else:
                    scan_results = run_python_fallback_scan(target_ip, ports_list)

            table = Table(title=f"[bold white]HASIL SCAN PORT TARGET: {target_ip}[/bold white]", border_style="red", expand=True)
            table.add_column("Port", style="bold red", width=8)
            table.add_column("State", style="bold green", width=10)
            table.add_column("Layanan", style="bold white", width=18)
            table.add_column("Level Risiko", style="bold yellow", width=14)
            table.add_column("Keterangan", style="dim white")

            if scan_results:
                for p in scan_results:
                    table.add_row(
                        str(p["port"]),
                        p["state"].upper(),
                        p["service"],
                        p["risk_level"],
                        p["description"]
                    )
                console.print(table)
            else:
                console.print(f"\n[bold green]✔ Tidak ada port terbuka dari daftar yang dipindai pada {target_ip}.[/bold green]")
            pause()
