"""
WiFi Intruder Alert & Whitelist Manager
Tracks trusted household devices. Alerts when an unknown/unauthorized device
(rogue neighbor or WiFi password cracker) connects to the WiFi network.
"""
from typing import List, Dict, Any, Optional
from core.utils import load_config, save_config, get_default_gateway, get_local_ip
from modules.net_optimizer.lan_scanner import scan_local_network, lookup_vendor


def get_trusted_devices() -> List[Dict[str, str]]:
    """Loads trusted device whitelist from config.json."""
    cfg = load_config()
    return cfg.get("security", {}).get("whitelist", [])


def save_trusted_devices(whitelist: List[Dict[str, str]]) -> bool:
    """Saves updated whitelist back to config.json."""
    cfg = load_config()
    if "security" not in cfg:
        cfg["security"] = {}
    cfg["security"]["whitelist"] = whitelist
    return save_config(cfg)


def add_to_whitelist(mac: str, alias_name: str, ip: str = "") -> bool:
    """Adds a device to the trusted whitelist."""
    clean_mac = mac.lower().replace("-", ":").strip()
    whitelist = get_trusted_devices()

    # Check if already in whitelist
    for item in whitelist:
        if item.get("mac", "").lower() == clean_mac:
            item["name"] = alias_name
            if ip:
                item["ip"] = ip
            return save_trusted_devices(whitelist)

    whitelist.append({
        "mac": clean_mac,
        "name": alias_name,
        "ip": ip,
        "vendor": lookup_vendor(clean_mac)
    })
    return save_trusted_devices(whitelist)


def remove_from_whitelist(mac: str) -> bool:
    """Removes a device from the trusted whitelist."""
    clean_mac = mac.lower().replace("-", ":").strip()
    whitelist = get_trusted_devices()
    new_list = [d for d in whitelist if d.get("mac", "").lower() != clean_mac]
    return save_trusted_devices(new_list)


def check_for_intruders() -> Dict[str, Any]:
    """
    Scans the local WiFi network and categorizes connected hosts into
    Trusted (Whitelist) vs Intruder (Unrecognized).
    """
    devices = scan_local_network()
    whitelist = get_trusted_devices()
    trusted_macs = {d.get("mac", "").lower(): d.get("name", "Perangkat Terdaftar") for d in whitelist}

    trusted_list = []
    intruders_list = []

    gw_ip = get_default_gateway()
    my_ip = get_local_ip()

    for dev in devices:
        mac = dev.get("mac", "").lower()
        ip = dev.get("ip", "")

        # Auto-trust gateway router and current host if not explicitly listed
        if ip == gw_ip or ip == my_ip:
            alias = "Router Gateway" if ip == gw_ip else "Host Ini (Laptop/HP)"
            dev["alias"] = trusted_macs.get(mac, alias)
            dev["is_trusted"] = True
            trusted_list.append(dev)
            continue

        if mac in trusted_macs:
            dev["alias"] = trusted_macs[mac]
            dev["is_trusted"] = True
            trusted_list.append(dev)
        else:
            dev["alias"] = "Perangkat Asing / Tidak Dikenal"
            dev["is_trusted"] = False
            intruders_list.append(dev)

    return {
        "total_connected": len(devices),
        "trusted_count": len(trusted_list),
        "intruder_count": len(intruders_list),
        "trusted_devices": trusted_list,
        "intruders": intruders_list
    }
