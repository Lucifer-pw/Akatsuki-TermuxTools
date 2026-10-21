"""
TUI Interface for Network & Bandwidth Optimizer
"""
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from core.theme import console
from core.utils import clear_screen, pause, get_default_gateway, get_local_ip
from .dns_bench import run_dns_benchmark
from .ping_keeper import run_ping_keepalive
from .mtu_finder import find_optimal_mtu
from .lan_scanner import scan_local_network
from .bandwidth_monitor import run_bandwidth_monitor
from .mtu_finder import find_optimal_mtu
from .lan_scanner import scan_local_network


def render_dns_results(results: list) -> None:
    """Renders DNS benchmark results in a styled Rich Table."""
    table = Table(
        title="[bold white]⚡ HASIL BENCHMARK KECEPATAN DNS (RESOLVER SPEED)[/bold white]",
        border_style="red",
        expand=True
    )
    table.add_column("Rank", style="bold red", width=6, justify="center")
    table.add_column("Penyedia DNS", style="bold white", width=28)
    table.add_column("IP Server", style="cyan", width=16)
    table.add_column("Rata-rata Latensi", style="yellow", justify="right")
    table.add_column("Rentang (Min - Max)", style="dim white", justify="center")
    table.add_column("Private DNS (DoH/DoT)", style="green")

    for rank, item in enumerate(results, start=1):
        if item["success"]:
            avg_str = f"[bold green]{item['avg_ms']} ms[/bold green]" if item['avg_ms'] < 30 else f"{item['avg_ms']} ms"
            range_str = f"{item['min_ms']} - {item['max_ms']} ms"
            medal = "🥇 " if rank == 1 else ("🥈 " if rank == 2 else ("🥉 " if rank == 3 else f"#{rank}"))
            table.add_row(medal, item["name"], item["ip"], avg_str, range_str, item["doh"])
        else:
            table.add_row(f"#{rank}", item["name"], item["ip"], "[bold red]TIMEOUT[/bold red]", "-", item["doh"])

    console.print(table)

    # Highlight recommendation
    if results and results[0]["success"]:
        best = results[0]
        console.print(Panel(
            f"[bold green]✔ REKOMENDASI TERBAIK:[/bold green] [bold white]{best['name']} ({best['ip']})[/bold white]\n"
            f"[white]Latensi rata-rata: [bold green]{best['avg_ms']} ms[/bold green][/white]\n"
            f"[dim white]Untuk mengaktifkan DNS ini di Android: Buka Settings -> Network & Internet -> Private DNS -> ketik: [/dim white]"
            f"[bold cyan]{best['doh']}[/bold cyan]",
            border_style="green",
            title="[bold white]PANDUAN OPTIMASI ANDROID[/bold white]"
        ))


def run_network_module() -> None:
    """Main interactive runner for Network & Bandwidth Optimizer."""
    gw_ip = get_default_gateway()
    my_ip = get_local_ip()

    while True:
        clear_screen()
        header = Panel(
            "[bold red]AKATSUKI NETWORK & BANDWIDTH OPTIMIZER[/bold red]\n"
            "[white]Diagnostik, penstabil latensi, penguji DNS tercepat, dan monitor jaringan Termux.[/white]\n"
            f"[dim white]IP Anda: [bold white]{my_ip}[/bold white] | Router Gateway: [bold red]{gw_ip}[/bold red][/dim white]",
            border_style="red",
            title="[bold white]MODUL 3[/bold white]"
        )
        console.print(header)

        menu_table = Table(show_header=False, border_style="red", expand=True, box=None)
        menu_table.add_column("Key", style="bold red", width=6, justify="center")
        menu_table.add_column("Fitur Optimasi", style="bold white")

        menu_table.add_row("[1]", "⚡ [bold white]Benchmark Multi-DNS[/bold white] (Uji & Temukan DNS Tercepat)")
        menu_table.add_row("[2]", "📡 [bold white]Ping Keep-Alive Daemon[/bold white] (Cegah WiFi Sleep & Monitor Latensi)")
        menu_table.add_row("[3]", "📦 [bold white]MTU Path Finder[/bold white] (Uji Ukuran Paket Maksimal Tanpa Fragmentasi)")
        menu_table.add_row("[4]", "🔍 [bold white]LAN Device Scanner[/bold white] (Pindai Perangkat Aktif di WiFi Anda)")
        menu_table.add_row("[5]", "📊 [bold white]Bandwidth Activity Monitor[/bold white] (Siapa yang Bikin WiFi Lemot?)")
        menu_table.add_row("[0]", "🚪 Kembali ke Menu Utama")

        console.print(Panel(menu_table, title="[bold white]OPSI OPTIMASI JARINGAN[/bold white]", border_style="red"))

        try:
            choice = input("\n[Network Action] > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break

        elif choice == "1":
            # DNS Benchmark
            console.print(f"\n[bold white]Menjalankan pengujian resolusi query ke daftar server DNS...[/bold white]")
            with console.status("[bold red]Menguji latensi query DNS...[/bold red]", spinner="dots"):
                res = run_dns_benchmark(gateway_ip=gw_ip, rounds=3)
            console.print()
            render_dns_results(res)
            pause()

        elif choice == "2":
            # Ping Keep Alive
            console.print(f"\n[bold white]Masukkan target IP/Host keep-alive (Default: 1.1.1.1):[/bold white]")
            target = input("[Target (1.1.1.1)] > ").strip() or "1.1.1.1"
            console.print(f"[bold white]Masukkan interval detik (Default: 1.5):[/bold white]")
            interval_str = input("[Interval detik] > ").strip()
            interval = float(interval_str) if interval_str.replace(".", "", 1).isdigit() else 1.5

            clear_screen()
            run_ping_keepalive(target=target, interval=interval)
            pause()

        elif choice == "3":
            # MTU Finder
            console.print(f"\n[bold white]Menguji batas MTU koneksi tanpa fragmentasi...[/bold white]")
            with console.status("[bold red]Mengirim probe ICMP dengan flag Don't Fragment (DF)...[/bold red]", spinner="bouncingBar"):
                mtu_res = find_optimal_mtu("1.1.1.1")

            table = Table(title="[bold white]📦 HASIL ANALISIS MTU JARINGAN[/bold white]", border_style="red", expand=True)
            table.add_column("Parameter", style="bold red", width=24)
            table.add_column("Hasil Pengujian", style="bold white")

            table.add_row("Nilai MTU Optimal", f"[bold green]{mtu_res['optimal_mtu']}[/bold green] bytes")
            table.add_row("Ukuran Payload ICMP", f"{mtu_res['optimal_payload']} bytes (+28 header bytes)")
            table.add_row("Klasifikasi Jaringan", mtu_res["status"])
            table.add_row("Rekomendasi", mtu_res["recommendation"])

            console.print()
            console.print(table)
            pause()

        elif choice == "5":
            # Bandwidth Activity Monitor
            console.print(f"\n[bold white]Menganalisis aktivitas bandwidth semua perangkat di WiFi {my_ip}/24...[/bold white]")
            console.print("[dim white]Proses ini memindai latensi & port setiap perangkat (~10-30 detik)...[/dim white]")
            with console.status("[bold red]Memindai aktivitas jaringan setiap perangkat...[/bold red]", spinner="bouncingBar"):
                bw_results = run_bandwidth_monitor(my_ip)

            if not bw_results:
                console.print("\n[bold yellow]Tidak ada perangkat lain yang terdeteksi aktif di jaringan.[/bold yellow]")
                pause()
                continue

            # Main bandwidth table
            table = Table(
                title=f"[bold white]📊 BANDWIDTH ACTIVITY MONITOR ({len(bw_results)} Perangkat)[/bold white]",
                border_style="red",
                expand=True
            )
            table.add_column("No", style="bold red", width=4, justify="center")
            table.add_column("IP Address", style="bold white", width=15)
            table.add_column("Merk / Device", style="cyan", width=18)
            table.add_column("Latency", style="yellow", width=10, justify="right")
            table.add_column("Aktivitas Terdeteksi", style="bold white", width=22)
            table.add_column("Beban WiFi", justify="center", width=14)

            for idx, dev in enumerate(bw_results, start=1):
                lat_str = f"{dev['latency_ms']:.0f} ms" if dev['latency_ms'] >= 0 else "Timeout"
                if dev['latency_ms'] >= 0 and dev['latency_ms'] < 5:
                    lat_display = f"[bold green]{lat_str}[/bold green]"
                elif dev['latency_ms'] >= 0 and dev['latency_ms'] < 50:
                    lat_display = f"[yellow]{lat_str}[/yellow]"
                elif dev['latency_ms'] >= 0:
                    lat_display = f"[bold red]{lat_str}[/bold red]"
                else:
                    lat_display = f"[dim white]{lat_str}[/dim white]"

                table.add_row(
                    str(idx),
                    dev["ip"],
                    dev["vendor"],
                    lat_display,
                    dev["activity"],
                    dev["bw_badge"]
                )

            console.print()
            console.print(table)

            # Summary panel
            if bw_results:
                heaviest = bw_results[0]
                if heaviest["bw_score"] >= 40:
                    console.print(Panel(
                        f"[bold red]⚠ PERANGKAT PALING BOROS BANDWIDTH:[/bold red]\n"
                        f"[bold white]IP: {heaviest['ip']}[/bold white] ({heaviest['vendor']})\n"
                        f"[white]Aktivitas: [bold yellow]{heaviest['activity']}[/bold yellow][/white]\n"
                        f"[white]Skor Beban: {heaviest['bw_badge']}[/white]\n\n"
                        f"[dim white]Perangkat ini kemungkinan besar penyebab WiFi Anda melambat.[/dim white]",
                        border_style="red",
                        title="[bold white]TERSANGKA UTAMA WIFI LEMOT[/bold white]"
                    ))
                else:
                    console.print(Panel(
                        f"[bold green]✔ Semua perangkat terdeteksi dalam kondisi ringan/idle.[/bold green]\n"
                        f"[dim white]Jika WiFi masih lambat, kemungkinan masalahnya ada di sisi ISP (IndiHome) atau kuota FUP.[/dim white]",
                        border_style="green",
                        title="[bold white]STATUS JARINGAN[/bold white]"
                    ))

            pause()

        elif choice == "4":
            # LAN Scanner
            console.print(f"\n[bold white]Memindai perangkat aktif pada subnet lokal {my_ip}/24...[/bold white]")
            with console.status("[bold red]Memindai host lokal secara asinkron...[/bold red]", spinner="dots"):
                devices = scan_local_network(my_ip)

            table = Table(
                title=f"[bold white]🔍 NETCUT-STYLE WIFI SCANNER ({len(devices)} Perangkat Terdeteksi)[/bold white]",
                border_style="red",
                expand=True
            )
            table.add_column("No", style="bold red", width=4, justify="center")
            table.add_column("IP Address", style="bold white", width=16)
            table.add_column("MAC Address", style="yellow", width=19)
            table.add_column("Merk / Vendor", style="bold cyan", width=24)
            table.add_column("Peran / Device", style="dim white")
            table.add_column("Status", style="green", width=14, justify="center")

            for idx, dev in enumerate(devices, start=1):
                table.add_row(
                    str(idx),
                    dev["ip"],
                    dev["mac"],
                    dev["vendor"],
                    dev["role"],
                    dev["status"]
                )

            console.print()
            console.print(table)
            pause()

        elif choice == "5":
            # Bandwidth Activity Monitor
            console.print(f"\n[bold white]Menganalisis aktivitas bandwidth semua perangkat di WiFi {my_ip}/24...[/bold white]")
            console.print("[dim white]Proses ini memindai latensi & port setiap perangkat (~10-30 detik)...[/dim white]")
            with console.status("[bold red]Memindai aktivitas jaringan setiap perangkat...[/bold red]", spinner="bouncingBar"):
                bw_results = run_bandwidth_monitor(my_ip)

            if not bw_results:
                console.print("\n[bold yellow]Tidak ada perangkat lain yang terdeteksi aktif di jaringan.[/bold yellow]")
                pause()
                continue

            # Main bandwidth table
            table = Table(
                title=f"[bold white]📊 BANDWIDTH ACTIVITY MONITOR ({len(bw_results)} Perangkat)[/bold white]",
                border_style="red",
                expand=True
            )
            table.add_column("No", style="bold red", width=4, justify="center")
            table.add_column("IP Address", style="bold white", width=15)
            table.add_column("Merk / Device", style="cyan", width=18)
            table.add_column("Latency", style="yellow", width=10, justify="right")
            table.add_column("Aktivitas Terdeteksi", style="bold white", width=22)
            table.add_column("Beban WiFi", justify="center", width=14)

            for idx, dev in enumerate(bw_results, start=1):
                lat_str = f"{dev['latency_ms']:.0f} ms" if dev['latency_ms'] >= 0 else "Timeout"
                if dev['latency_ms'] >= 0 and dev['latency_ms'] < 5:
                    lat_display = f"[bold green]{lat_str}[/bold green]"
                elif dev['latency_ms'] >= 0 and dev['latency_ms'] < 50:
                    lat_display = f"[yellow]{lat_str}[/yellow]"
                elif dev['latency_ms'] >= 0:
                    lat_display = f"[bold red]{lat_str}[/bold red]"
                else:
                    lat_display = f"[dim white]{lat_str}[/dim white]"

                table.add_row(
                    str(idx),
                    dev["ip"],
                    dev["vendor"],
                    lat_display,
                    dev["activity"],
                    dev["bw_badge"]
                )

            console.print()
            console.print(table)

            # Summary panel
            if bw_results:
                heaviest = bw_results[0]
                if heaviest["bw_score"] >= 40:
                    console.print(Panel(
                        f"[bold red]⚠ PERANGKAT PALING BOROS BANDWIDTH:[/bold red]\n"
                        f"[bold white]IP: {heaviest['ip']}[/bold white] ({heaviest['vendor']})\n"
                        f"[white]Aktivitas: [bold yellow]{heaviest['activity']}[/bold yellow][/white]\n"
                        f"[white]Skor Beban: {heaviest['bw_badge']}[/white]\n\n"
                        f"[dim white]Perangkat ini kemungkinan besar penyebab WiFi Anda melambat.[/dim white]",
                        border_style="red",
                        title="[bold white]TERSANGKA UTAMA WIFI LEMOT[/bold white]"
                    ))
                else:
                    console.print(Panel(
                        f"[bold green]✔ Semua perangkat terdeteksi dalam kondisi ringan/idle.[/bold green]\n"
                        f"[dim white]Jika WiFi masih lambat, kemungkinan masalahnya ada di sisi ISP (IndiHome) atau kuota FUP.[/dim white]",
                        border_style="green",
                        title="[bold white]STATUS JARINGAN[/bold white]"
                    ))

            pause()
