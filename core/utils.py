"""
System, Network, and Environment Utilities
Designed for Termux (Android) and cross-platform compatibility.
"""
import os
import sys
import json
import socket
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"
EXAMPLE_CONFIG = Path(__file__).resolve().parent.parent / "config.example.json"


def is_termux() -> bool:
    """Checks whether the current environment is running inside Android Termux."""
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix or os.path.exists("/data/data/com.termux")


def load_config() -> Dict[str, Any]:
    """Loads configuration from config.json with fallback to default values."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if EXAMPLE_CONFIG.exists():
        try:
            with open(EXAMPLE_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "router": {
            "gateway_ip": "auto",
            "port": 80,
            "model": "zte",
            "username": "user",
            "password": "user1234",
            "timeout": 5
        },
        "network": {
            "keep_alive_target": "1.1.1.1",
            "keep_alive_interval": 2.0,
            "dns_servers": [
                {"name": "Cloudflare DNS", "ip": "1.1.1.1"},
                {"name": "Google Public DNS", "ip": "8.8.8.8"}
            ],
            "mtu_test_host": "1.1.1.1"
        },
        "osint": {
            "default_region": "ID",
            "numverify_api_key": ""
        }
    }


def save_config(config: Dict[str, Any]) -> bool:
    """Saves dictionary configuration back to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def get_local_ip() -> str:
    """Detects the primary local IP address of the device."""
    try:
        # UDP dummy connect (doesn't send actual packet, just binds outbound interface)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_default_gateway() -> str:
    """
    Detects the default gateway IP (usually the WiFi router 192.168.1.1 / 192.168.100.1).
    Supports Linux/Termux routing tables and Windows.
    """
    # 1. Check /proc/net/route (Standard Linux & Android)
    if os.path.exists("/proc/net/route"):
        try:
            with open("/proc/net/route", "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[1] == "00000000": # default route
                        gw_hex = parts[2]
                        # Convert little-endian hex to IP string
                        ip_parts = [str(int(gw_hex[i:i+2], 16)) for i in (6, 4, 2, 0)]
                        gw_ip = ".".join(ip_parts)
                        if gw_ip != "0.0.0.0":
                            return gw_ip
        except Exception:
            pass

    # 2. Try 'ip route' command (Available on most Linux/Termux setups)
    try:
        proc = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if proc.returncode == 0:
            tokens = proc.stdout.split()
            if "via" in tokens:
                idx = tokens.index("via")
                if idx + 1 < len(tokens):
                    return tokens[idx + 1]
    except Exception:
        pass

    # 3. Windows netstat / ipconfig fallback
    if sys.platform == "win32":
        try:
            proc = subprocess.run(
                ["netstat", "-rn"],
                capture_output=True,
                text=True,
                timeout=1
            )
            for line in proc.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                    return parts[2]
        except Exception:
            pass

    # Default fallback
    return "192.168.1.1"


def get_battery_info() -> str:
    """Fetches battery status if running on Termux with termux-api installed."""
    if is_termux():
        try:
            proc = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                percent = data.get("percentage", "?")
                status = data.get("status", "")
                return f"{percent}% ({status})"
        except Exception:
            pass
    return "N/A"


def get_network_type() -> str:
    """Detects network interface connection type."""
    local_ip = get_local_ip()
    if local_ip.startswith("192.168.") or local_ip.startswith("10.") or local_ip.startswith("172."):
        return "WiFi / LAN"
    elif local_ip == "127.0.0.1":
        return "Offline"
    return "Mobile / Cellular"


def get_system_summary() -> Dict[str, str]:
    """Aggregates system info for the header banner."""
    return {
        "gateway": get_default_gateway(),
        "local_ip": get_local_ip(),
        "net_type": get_network_type(),
        "battery": get_battery_info(),
        "platform": "Termux (Android)" if is_termux() else sys.platform
    }


def clear_screen() -> None:
    """Clears the terminal screen cross-platform."""
    os.system("cls" if sys.platform == "win32" else "clear")


def pause(message: str = "Press Enter to return to main menu...") -> None:
    """Halts execution until the user presses Enter."""
    input(f"\n{message}")
