"""
Ping Keep-Alive Daemon & Real-time Latency Monitor
Prevents Android Termux WiFi power-saving sleep and tracks connection stability.
"""
import sys
import time
import subprocess
import re
from typing import Optional, Tuple
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from core.theme import console


def measure_single_ping(target: str, timeout_sec: int = 2) -> Tuple[bool, float]:
    """
    Executes a single ICMP ping and returns (is_alive, latency_ms).
    Cross-platform for Linux/Android Termux and Windows.
    """
    if sys.platform == "win32":
        cmd = ["ping", "-n", "1", "-w", str(timeout_sec * 1000), target]
    else:
        # Linux & Android Termux
        cmd = ["ping", "-c", "1", "-W", str(timeout_sec), target]

    try:
        start_t = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec + 1)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        if proc.returncode == 0:
            # Try to extract actual ICMP round-trip time from ping output
            # Linux: "time=12.4 ms"
            # Windows: "time=12ms" or "tempo=12ms"
            match = re.search(r'(?:time|tempo|waktu)[=<](\d+(?:\.\d+)?)\s*ms', proc.stdout, re.I)
            if match:
                return True, float(match.group(1))
            return True, round(elapsed_ms, 1)
        return False, 0.0
    except Exception:
        return False, 0.0


def run_ping_keepalive(target: str = "1.1.1.1", interval: float = 1.5) -> None:
    """
    Runs the keep-alive monitor in a live Rich loop.
    Exits cleanly when user presses Ctrl+C.
    """
    console.print(Panel(
        f"[bold red]✦ PING KEEP-ALIVE DAEMON AKTIF[/bold red]\n"
        f"[white]Target: [bold red]{target}[/bold red] | Interval: [bold white]{interval}s[/bold white][/white]\n"
        f"[dim white]Fungsi: Mencegah Android sleep mode pada radio WiFi dan memonitor jitter jaringan.[/dim white]\n"
        f"[bold yellow]Tekan Ctrl+C kapan saja untuk berhenti dan kembali ke menu.[/bold yellow]",
        border_style="red"
    ))

    packets_sent = 0
    packets_recv = 0
    latencies = []

    try:
        while True:
            packets_sent += 1
            success, latency = measure_single_ping(target)
            
            if success:
                packets_recv += 1
                latencies.append(latency)
                loss_pct = round(((packets_sent - packets_recv) / packets_sent) * 100, 1)
                avg_ms = round(sum(latencies) / len(latencies), 1)
                min_ms = round(min(latencies), 1)
                max_ms = round(max(latencies), 1)

                # Color-code latency
                if latency < 35:
                    lat_style = "[bold green]"
                elif latency < 90:
                    lat_style = "[bold yellow]"
                else:
                    lat_style = "[bold red]"

                console.print(
                    f"[dim]#{packets_sent:04d}[/dim] "
                    f"[white]Keep-Alive to[/white] [bold red]{target}[/bold red]: "
                    f"RTT={lat_style}{latency:.1f} ms[/] | "
                    f"[dim]Min:[/dim] [green]{min_ms}[/green] [dim]Avg:[/dim] [yellow]{avg_ms}[/yellow] [dim]Max:[/dim] [red]{max_ms}[/red] ms | "
                    f"[dim]Loss:[/dim] [cyan]{loss_pct}%[/cyan]"
                )
            else:
                loss_pct = round(((packets_sent - packets_recv) / packets_sent) * 100, 1)
                console.print(
                    f"[dim]#{packets_sent:04d}[/dim] "
                    f"[white]Keep-Alive to[/white] [bold red]{target}[/bold red]: "
                    f"[bold red]REQUEST TIMEOUT (Packet Loss)[/bold red] | "
                    f"[dim]Loss:[/dim] [red]{loss_pct}%[/red]"
                )

            time.sleep(interval)

    except KeyboardInterrupt:
        console.print(f"\n[bold yellow]Keep-Alive Daemon dihentikan oleh pengguna.[/bold yellow]")
        if packets_sent > 0:
            loss_pct = round(((packets_sent - packets_recv) / packets_sent) * 100, 1)
            console.print(
                f"[bold white]Statistik Akhir:[/bold white] Terkirim: {packets_sent}, Diterima: {packets_recv}, "
                f"Packet Loss: {loss_pct}%\n"
            )
