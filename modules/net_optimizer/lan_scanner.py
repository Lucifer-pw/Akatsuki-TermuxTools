"""
NetCut-style Local WiFi & LAN Device Scanner
Discovers all connected devices on the local subnet (/24) including IP, MAC address,
hardware vendor / brand (OUI), and device role (Router, Host, Mobile Phone, IoT).
Compatible with Android Termux and Windows.
"""
import os
import sys
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from core.utils import get_local_ip, get_default_gateway

# Common OUI Vendor database (Top smartphone, router, PC & IoT brands)
OUI_VENDORS = {
    # FiberHome, ZTE, Huawei
    "bc:46:32": "FiberHome Telecomm",
    "48:d5:39": "FiberHome Telecomm",
    "90:94:92": "FiberHome Telecomm",
    "00:1e:73": "ZTE Corporation",
    "00:23:89": "ZTE Corporation",
    "d4:6e:0e": "ZTE Corporation",
    "ec:22:80": "ZTE Corporation",
    "00:18:82": "Huawei Technologies",
    "00:25:9e": "Huawei Technologies",
    "24:69:68": "Huawei Technologies",
    "4c:54:99": "Huawei Device",
    "60:de:44": "Huawei Device",
    # Vivo & Oppo & Realme
    "04:42:1a": "Vivo Mobile (HP)",
    "3c:07:54": "Vivo Mobile (HP)",
    "78:02:f8": "Vivo Mobile (HP)",
    "bc:54:51": "Vivo Mobile (HP)",
    "00:bb:60": "OPPO / Realme (HP)",
    "2c:5b:f7": "OPPO / Realme (HP)",
    "38:71:de": "OPPO / Realme (HP)",
    "78:1f:db": "OPPO / Realme (HP)",
    "90:2b:34": "OPPO / Realme (HP)",
    # Xiaomi & Redmi
    "70:2c:1f": "Xiaomi / Redmi (HP)",
    "ac:e0:10": "Xiaomi / Redmi (HP)",
    "f4:60:e2": "Xiaomi / Redmi (HP)",
    "64:cc:2e": "Xiaomi / Redmi (HP)",
    "74:23:44": "Xiaomi / Redmi (HP)",
    "34:80:0d": "Xiaomi / Redmi (HP)",
    # Samsung
    "00:1a:2b": "Samsung Electronics",
    "24:4b:fe": "Samsung Electronics",
    "50:01:d9": "Samsung Electronics",
    "5c:0a:5b": "Samsung Galaxy (HP)",
    "e8:50:8b": "Samsung Galaxy (HP)",
    "88:30:8a": "Samsung Galaxy (HP)",
    # Apple
    "f0:18:98": "Apple (iPhone / Mac)",
    "3c:22:fb": "Apple (iPhone / Mac)",
    "a4:83:e7": "Apple (iPhone / Mac)",
    "f8:ff:c2": "Apple (iPhone / Mac)",
    "00:cd:fe": "Apple (iPhone / Mac)",
    "14:98:77": "Apple (iPhone / Mac)",
    # TP-Link, Tenda, D-Link, Asus
    "00:1d:0f": "TP-Link Technologies",
    "14:75:90": "TP-Link Technologies",
    "94:d9:b3": "TP-Link Technologies",
    "50:d4:f7": "TP-Link Technologies",
    "c8:3a:35": "Tenda Technology",
    "00:22:6b": "AsusTek Computer",
    "00:1e:58": "D-Link Corporation",
    # PC Network Cards & Smart Home IoT
    "34:e6:ad": "Intel Corporation",
    "48:2a:e3": "Intel Corporation",
    "ac:bc:32": "Intel Corporation",
    "a4:bb:6d": "Realtek Semiconductor",
    "b0:6e:bf": "Realtek Semiconductor",
    "24:0a:c4": "Espressif (Smart Bulb/IoT)",
    "30:ae:a4": "Espressif (Smart Plug/IoT)",
    "84:f3:eb": "Espressif (Smart Home IoT)",
    "b8:27:eb": "Raspberry Pi",
    "dc:a6:32": "Raspberry Pi"
}


def lookup_vendor(mac: str) -> str:
    """Resolves MAC address prefix to manufacturer brand."""
    if not mac or mac == "00:00:00:00:00:00":
        return "Unknown Device"

    clean_mac = mac.lower().replace("-", ":")
    prefix = ":".join(clean_mac.split(":")[:3])

    if prefix in OUI_VENDORS:
        return OUI_VENDORS[prefix]

    # Check for Randomized / Private MAC address (Standard on Android 10+ and iOS 14+)
    # If the 2nd least significant bit of the first byte is 1 (e.g. x2, x6, xA, xE)
    first_byte_hex = clean_mac.split(":")[0]
    if len(first_byte_hex) == 2:
        try:
            byte_val = int(first_byte_hex, 16)
            if byte_val & 0b00000010:
                return "HP / Device (Private/Random MAC)"
        except Exception:
            pass

    return "Perangkat Terhubung"


def get_system_arp_table() -> Dict[str, str]:
    """Reads ARP table mapping IP -> MAC address cross-platform."""
    arp_map = {}

    # 1. Linux & Android Termux (/proc/net/arp)
    if os.path.exists("/proc/net/arp"):
        try:
            with open("/proc/net/arp", "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 4 and parts[3] != "00:00:00:00:00:00":
                        ip = parts[0]
                        mac = parts[3].lower()
                        arp_map[ip] = mac
            if arp_map:
                return arp_map
        except Exception:
            pass

    # 2. Windows / Linux 'arp -a' command
    try:
        proc = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=2)
        for line in proc.stdout.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F[:-]{11,17})\s+(\w+)?", line)
            if match:
                ip = match.group(1)
                mac = match.group(2).replace("-", ":").lower()
                # Exclude broadcast & multicast
                if not ip.endswith(".255") and not ip.startswith("224.") and not ip.startswith("239.") and mac != "ff:ff:ff:ff:ff:ff":
                    arp_map[ip] = mac
    except Exception:
        pass

    return arp_map


def probe_single_ip(ip: str, timeout: float = 0.2) -> bool:
    """Quickly probes an IP via socket to populate ARP cache."""
    # Probe common port 80 or 443 or 53
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect_ex((ip, 80))
        s.close()
        return True
    except Exception:
        s.close()
        return False


def scan_local_network(base_ip: Optional[str] = None, max_threads: int = 60) -> List[Dict[str, Any]]:
    """
    Performs a NetCut-style WiFi subnet sweep:
    1. Sends concurrent connection probes across subnet 1-254 to populate the OS ARP table.
    2. Reads the ARP table for real physical MAC addresses.
    3. Resolves hardware manufacturer / brand.
    4. Identifies the Router Gateway and the host device.
    """
    if not base_ip or base_ip == "127.0.0.1":
        base_ip = get_local_ip()

    gw_ip = get_default_gateway()
    my_ip = get_local_ip()

    parts = (base_ip if base_ip != "127.0.0.1" else gw_ip).split(".")
    if len(parts) != 4:
        parts = ["192", "168", "1", "1"]

    subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."
    candidate_ips = [f"{subnet_prefix}{i}" for i in range(1, 255)]

    # 1. Concurrent sweep to warm up ARP table
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        list(executor.map(probe_single_ip, candidate_ips))

    # 2. Read refreshed ARP table
    arp_table = get_system_arp_table()

    active_devices = []
    # Ensure gateway and current device are tracked even if not in ARP table
    discovered_ips = set(arp_table.keys())
    discovered_ips.add(gw_ip)
    discovered_ips.add(my_ip)

    for ip in discovered_ips:
        if not ip.startswith(subnet_prefix):
            continue

        mac = arp_table.get(ip, "Tidak Diketahui")
        vendor = lookup_vendor(mac)

        role = "Perangkat WiFi Aktif"
        badge = "[green]● Online[/green]"

        if ip == gw_ip:
            role = "👑 Router / Gateway (WiFi AP)"
            if vendor == "Perangkat Terhubung" or vendor == "Unknown Device":
                vendor = "FiberHome / ZTE ONT"
        elif ip == my_ip:
            role = "💻 Perangkat Anda (Host Ini)"
            badge = "[bold cyan]● Ini Perangkat Anda[/bold cyan]"

        active_devices.append({
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "role": role,
            "status": badge
        })

    # Sort numerically by IP octet
    active_devices.sort(key=lambda x: int(x["ip"].split(".")[-1]))
    return active_devices
