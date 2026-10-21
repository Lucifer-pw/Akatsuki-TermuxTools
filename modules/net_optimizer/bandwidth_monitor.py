"""
WiFi Bandwidth Activity Monitor (NetCut-Style)
Monitors network activity of all connected devices in real-time.
Estimates which device is consuming bandwidth by measuring:
- ARP response latency (slower = heavier load)
- Connection activity frequency
- Port activity scoring
Works WITHOUT router login - purely from local network observation.
"""
import os
import sys
import time
import socket
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Tuple
from core.utils import get_local_ip, get_default_gateway
from .lan_scanner import get_system_arp_table, lookup_vendor, probe_single_ip


def measure_device_latency(ip: str, rounds: int = 3) -> float:
    """Measures average response latency to a device via ICMP ping (ms)."""
    if sys.platform == "win32":
        cmd = ["ping", "-n", str(rounds), "-w", "500", ip]
    else:
        cmd = ["ping", "-c", str(rounds), "-W", "1", ip]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=rounds + 2)
        # Extract average latency
        # Windows: "Average = 12ms"
        # Linux: "rtt min/avg/max/mdev = 1.2/3.4/5.6/1.1 ms"
        out = proc.stdout
        match_win = re.search(r'Average\s*=\s*(\d+)\s*ms', out, re.I)
        match_linux = re.search(r'/(\d+(?:\.\d+)?)/\d+(?:\.\d+)?/\d+(?:\.\d+)?\s*ms', out)

        if match_win:
            return float(match_win.group(1))
        elif match_linux:
            return float(match_linux.group(1))

        # If ping succeeded but couldn't parse, estimate from wall-clock
        if proc.returncode == 0:
            return round((rounds + 2) * 1000 / rounds, 1)
        return -1.0  # Unreachable
    except Exception:
        return -1.0


def scan_open_ports(ip: str, ports: List[int] = None, timeout: float = 0.15) -> List[int]:
    """Quick-scans common service ports on a device."""
    if ports is None:
        ports = [
            21,    # FTP (download)
            22,    # SSH
            80,    # HTTP (browsing)
            443,   # HTTPS (browsing/streaming)
            554,   # RTSP (video streaming/CCTV)
            1080,  # SOCKS Proxy
            1935,  # RTMP (live streaming)
            3128,  # HTTP Proxy
            3389,  # RDP
            5060,  # SIP (VoIP calls)
            5228,  # Android Push Notifications (Google Play)
            5900,  # VNC
            6881,  # BitTorrent
            8080,  # HTTP Alt (browsing/proxy)
            8443,  # HTTPS Alt
            9090,  # Web management
            51413, # BitTorrent (Transmission)
        ]

    open_ports = []
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
            s.close()
        except Exception:
            pass
    return open_ports


PORT_ACTIVITY_MAP = {
    21: ("FTP Download/Upload", "download"),
    22: ("SSH Remote Access", "other"),
    80: ("HTTP Browsing", "browsing"),
    443: ("HTTPS Browsing/Streaming", "browsing"),
    554: ("Video Streaming (RTSP/CCTV)", "streaming"),
    1080: ("SOCKS Proxy", "download"),
    1935: ("Live Streaming (RTMP)", "streaming"),
    3128: ("HTTP Proxy", "download"),
    3389: ("Remote Desktop (RDP)", "other"),
    5060: ("VoIP / Video Call", "streaming"),
    5228: ("Google Play / Push Notif", "browsing"),
    5900: ("VNC Remote Desktop", "other"),
    6881: ("BitTorrent / P2P Download", "download"),
    8080: ("HTTP Alt Browsing", "browsing"),
    8443: ("HTTPS Alt Browsing", "browsing"),
    9090: ("Web Management Panel", "other"),
    51413: ("BitTorrent (Transmission)", "download"),
}


def classify_activity(open_ports: List[int]) -> Tuple[str, str]:
    """
    Classifies what a device is likely doing based on open ports.
    Returns (activity_description, activity_category).
    """
    if not open_ports:
        return "Idle / Standby", "idle"

    activities = []
    categories = set()
    for port in open_ports:
        if port in PORT_ACTIVITY_MAP:
            desc, cat = PORT_ACTIVITY_MAP[port]
            activities.append(desc)
            categories.add(cat)

    if "download" in categories:
        return "Downloading / Torrent", "download"
    elif "streaming" in categories:
        return "Video Streaming / Call", "streaming"
    elif "browsing" in categories:
        return "Browsing / Social Media", "browsing"
    elif activities:
        return activities[0], "other"
    else:
        return "Aktif (Port Non-Standar)", "other"


def estimate_bandwidth_score(latency: float, open_ports: List[int]) -> Tuple[int, str]:
    """
    Estimates a relative bandwidth usage score (0-100) based on latency and port activity.
    Higher score = more likely consuming bandwidth.
    """
    score = 0

    # Latency-based scoring (higher latency on LAN = device is busy)
    if latency < 0:
        return 0, "[dim white]Offline[/dim white]"
    elif latency < 2:
        score += 10   # Very fast = idle
    elif latency < 10:
        score += 25
    elif latency < 50:
        score += 45
    elif latency < 100:
        score += 60
    else:
        score += 80   # Very slow = heavy bandwidth

    # Port-based scoring
    for port in open_ports:
        if port in (6881, 51413):    # Torrent
            score += 40
        elif port in (554, 1935, 5060):  # Streaming/VoIP
            score += 30
        elif port in (443, 80, 8080):    # Browsing
            score += 10
        elif port in (21, 1080, 3128):   # Download/Proxy
            score += 25

    score = min(score, 100)

    # Style badge
    if score >= 70:
        badge = f"[bold red]{score}% BERAT[/bold red]"
    elif score >= 40:
        badge = f"[bold yellow]{score}% Sedang[/bold yellow]"
    elif score > 0:
        badge = f"[bold green]{score}% Ringan[/bold green]"
    else:
        badge = f"[dim white]{score}% Idle[/dim white]"

    return score, badge


def run_bandwidth_monitor(base_ip: str = None) -> List[Dict[str, Any]]:
    """
    Main bandwidth activity scanner.
    1. Discovers devices via ARP sweep
    2. Measures latency to each
    3. Scans active ports
    4. Estimates bandwidth usage and activity type
    """
    if not base_ip or base_ip == "127.0.0.1":
        base_ip = get_local_ip()

    gw_ip = get_default_gateway()
    my_ip = get_local_ip()

    parts = (base_ip if base_ip != "127.0.0.1" else gw_ip).split(".")
    subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."
    candidate_ips = [f"{subnet_prefix}{i}" for i in range(1, 255)]

    # 1. ARP sweep
    with ThreadPoolExecutor(max_workers=60) as executor:
        list(executor.map(probe_single_ip, candidate_ips))

    arp_table = get_system_arp_table()
    discovered_ips = set(arp_table.keys())
    discovered_ips.add(gw_ip)

    # Filter to subnet only, exclude self
    target_ips = [ip for ip in discovered_ips
                  if ip.startswith(subnet_prefix) and ip != my_ip]

    results = []

    # 2. Measure latency and scan ports concurrently
    for ip in sorted(target_ips, key=lambda x: int(x.split(".")[-1])):
        mac = arp_table.get(ip, "Unknown")
        vendor = lookup_vendor(mac)
        latency = measure_device_latency(ip, rounds=2)
        open_ports = scan_open_ports(ip)
        activity, category = classify_activity(open_ports)
        score, badge = estimate_bandwidth_score(latency, open_ports)

        role = "Perangkat WiFi"
        if ip == gw_ip:
            role = "Router / Gateway"
            activity = "Gateway (Routing Traffic)"
            category = "router"

        results.append({
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "role": role,
            "latency_ms": latency,
            "open_ports": open_ports,
            "activity": activity,
            "category": category,
            "bw_score": score,
            "bw_badge": badge
        })

    # Sort by bandwidth score descending (heaviest user first)
    results.sort(key=lambda x: x["bw_score"], reverse=True)
    return results
