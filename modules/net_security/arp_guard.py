"""
Anti-NetCut & ARP Spoofing Guard (Live Sentinel)
Monitors the local ARP table continuously for ARP poisoning / MITM attacks.
Detects when an attacker attempts to spoof the gateway router's MAC address,
identifies the attacker's hardware address and IP, and can lock the gateway
with Static ARP binding for complete immunity.
"""
import sys
import time
import subprocess
import re
from typing import Dict, Any, Optional, Tuple
from core.utils import get_default_gateway, get_local_ip
from core.theme import console
from rich.panel import Panel
from rich.table import Table
from modules.net_optimizer.lan_scanner import get_system_arp_table, lookup_vendor


class ARPGuard:
    def __init__(self, gateway_ip: Optional[str] = None):
        self.gateway_ip = gateway_ip or get_default_gateway()
        self.trusted_gateway_mac: Optional[str] = None
        self.is_static_locked = False
        self.alerts_count = 0
        self.history = []

        # Acquire initial trusted gateway MAC
        self.refresh_trusted_gateway()

    def refresh_trusted_gateway(self) -> Optional[str]:
        """Reads current ARP table to establish initial trusted gateway MAC."""
        # Send a quick probe to gateway so ARP table is warm
        try:
            cmd = ["ping", "-n", "1", "-w", "500", self.gateway_ip] if sys.platform == "win32" else ["ping", "-c", "1", "-W", "1", self.gateway_ip]
            subprocess.run(cmd, capture_output=True, timeout=1.5)
        except Exception:
            pass

        arp = get_system_arp_table()
        if self.gateway_ip in arp:
            self.trusted_gateway_mac = arp[self.gateway_ip]
        return self.trusted_gateway_mac

    def check_arp_status(self) -> Dict[str, Any]:
        """
        Checks current ARP table for gateway anomalies.
        Returns status dict.
        """
        arp = get_system_arp_table()
        current_mac = arp.get(self.gateway_ip)

        if not current_mac:
            return {
                "status": "normal",
                "message": "Gateway belum tercatat di ARP cache.",
                "attacker_ip": None,
                "attacker_mac": None
            }

        # If we didn't have a trusted MAC yet, learn it
        if not self.trusted_gateway_mac:
            self.trusted_gateway_mac = current_mac
            return {
                "status": "normal",
                "message": f"Gateway MAC terdaftar: {current_mac}",
                "attacker_ip": None,
                "attacker_mac": None
            }

        # Check if gateway MAC changed to something else
        if current_mac != self.trusted_gateway_mac:
            # An attack is underway! Find who owns this new MAC
            attacker_ip = None
            for ip, mac in arp.items():
                if mac == current_mac and ip != self.gateway_ip:
                    attacker_ip = ip
                    break

            attacker_vendor = lookup_vendor(current_mac)
            self.alerts_count += 1
            return {
                "status": "under_attack",
                "message": "SERANGAN ARP SPOOFING / NETCUT TERDETEKSI!",
                "current_mac": current_mac,
                "trusted_mac": self.trusted_gateway_mac,
                "attacker_ip": attacker_ip or "Tidak diketahui (disamarkan)",
                "attacker_mac": current_mac,
                "attacker_vendor": attacker_vendor
            }

        return {
            "status": "normal",
            "message": f"Koneksi Aman. Gateway MAC valid ({current_mac})",
            "current_mac": current_mac,
            "trusted_mac": self.trusted_gateway_mac,
            "attacker_ip": None,
            "attacker_mac": None
        }

    def lock_static_arp(self) -> Tuple[bool, str]:
        """
        Locks gateway IP <-> MAC as a Static/Permanent entry.
        Immunizes device from NetCut attacks.
        Requires admin/root privileges on system.
        """
        if not self.trusted_gateway_mac:
            return False, "Tidak dapat mengunci: MAC gateway belum terdeteksi."

        mac_fmt = self.trusted_gateway_mac.replace(":", "-") if sys.platform == "win32" else self.trusted_gateway_mac

        if sys.platform == "win32":
            # Windows arp -s
            cmd = ["arp", "-s", self.gateway_ip, mac_fmt]
        else:
            # Linux / Android ip neigh
            cmd = ["ip", "neigh", "replace", self.gateway_ip, "lladdr", mac_fmt, "nud", "permanent"]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if proc.returncode == 0:
                self.is_static_locked = True
                return True, f"Berhasil mengunci Static ARP: {self.gateway_ip} -> {mac_fmt} (Kebal NetCut)"
            return False, f"Gagal mengunci: Perlu akses Administrator / Root ({proc.stderr.strip()})"
        except Exception as e:
            return False, f"Error sistem: {e}"


def run_arp_guard_monitor(interval_sec: float = 2.0) -> None:
    """Live interactive watcher loop."""
    guard = ARPGuard()

    console.print(Panel(
        f"[bold red]✦ ANTI-NETCUT & ARP SPOOFING SENTINEL[/bold red]\n"
        f"[white]Gateway Target: [bold red]{guard.gateway_ip}[/bold red] | MAC Terverifikasi: [bold green]{guard.trusted_gateway_mac or 'Scanning...'}[/bold green][/white]\n"
        f"[dim white]Fungsi: Memantau spoofing jaringan secara real-time dan mendeteksi penyerang.[/dim white]\n"
        f"[bold yellow]Tekan Ctrl+C kapan saja untuk berhenti dan kembali ke menu.[/bold yellow]",
        border_style="red"
    ))

    scan_round = 0
    try:
        while True:
            scan_round += 1
            res = guard.check_arp_status()

            if res["status"] == "under_attack":
                console.print(Panel(
                    f"[bold red]🚨 SERANGAN NETCUT / ARP SPOOFING TERDETEKSI! 🚨[/bold red]\n"
                    f"[white]MAC Asli Router : [bold green]{res['trusted_mac']}[/bold green][/white]\n"
                    f"[white]MAC Penyerang    : [bold red]{res['attacker_mac']}[/bold red] ({res.get('attacker_vendor', 'Unknown')})[/white]\n"
                    f"[white]IP Pelaku        : [bold yellow]{res['attacker_ip']}[/bold yellow][/white]\n"
                    f"[dim white]Pelaku sedang mencoba memutus / membajak koneksi internet Anda![/dim white]",
                    border_style="red"
                ))
            else:
                gw_mac = res.get("current_mac", "-")
                console.print(
                    f"[dim white]#{scan_round:04d}[/dim white] "
                    f"[bold green]✔ Status Aman[/bold green] | "
                    f"Gateway [white]{guard.gateway_ip}[/white] -> [bold cyan]{gw_mac}[/bold cyan] | "
                    f"Serangan: [green]0 Terdeteksi[/green]"
                )

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        console.print(f"\n[bold yellow]Monitoring Anti-NetCut dihentikan oleh pengguna.[/bold yellow]")
