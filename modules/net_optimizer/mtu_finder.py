"""
Optimal MTU (Maximum Transmission Unit) Path Finder
Calculates the maximum unfragmented packet size using ICMP Don't Fragment (DF) flags.
"""
import sys
import subprocess
from typing import Tuple, Dict, Any


def test_packet_size(target: str, size: int) -> bool:
    """
    Tests whether a packet of `size` bytes can traverse the link without fragmentation.
    Total MTU = size + 28 (IP + ICMP headers).
    """
    if sys.platform == "win32":
        # Windows: -f (Don't Fragment), -l (Buffer size)
        cmd = ["ping", "-n", "1", "-w", "1000", "-f", "-l", str(size), target]
    else:
        # Linux & Android: -M do (Don't Fragment), -s (Payload size)
        cmd = ["ping", "-c", "1", "-W", "1", "-M", "do", "-s", str(size), target]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        out = (proc.stdout + proc.stderr).lower()
        if "fragment" in out or "df set" in out or "too large" in out or proc.returncode != 0:
            return False
        return True
    except Exception:
        return False


def find_optimal_mtu(target: str = "1.1.1.1") -> Dict[str, Any]:
    """
    Performs a binary search between payload 1372 (MTU 1400) and 1472 (MTU 1500)
    to pinpoint the maximum non-fragmented packet size.
    """
    low_payload = 1372  # MTU 1400
    high_payload = 1472 # MTU 1500
    best_payload = None

    # First check if 1472 passes (Standard MTU 1500)
    if test_packet_size(target, high_payload):
        return {
            "optimal_payload": high_payload,
            "optimal_mtu": high_payload + 28,
            "status": "Standard Ethernet (MTU 1500)",
            "recommendation": "Koneksi Anda mendukung MTU standar 1500 secara optimal tanpa fragmentasi."
        }

    # Binary search for boundary
    left = low_payload
    right = high_payload
    while left <= right:
        mid = (left + right) // 2
        if test_packet_size(target, mid):
            best_payload = mid
            left = mid + 1 # Try larger
        else:
            right = mid - 1 # Too large, try smaller

    if best_payload is None:
        best_payload = 1372

    optimal_mtu = best_payload + 28

    if optimal_mtu == 1492:
        rec = "Koneksi Anda menggunakan PPPoE (IndiHome / Fiber). Nilai MTU 1492 adalah angka emas terbaik."
    elif optimal_mtu < 1492:
        rec = f"Jaringan terdeteksi mengalami overhead tunneling/VPN/seluler. Atur MTU ke {optimal_mtu} untuk menghindari packet drop."
    else:
        rec = f"Nilai MTU maksimal tanpa fragmentasi pada jalur ini adalah {optimal_mtu}."

    return {
        "optimal_payload": best_payload,
        "optimal_mtu": optimal_mtu,
        "status": f"Optimal MTU: {optimal_mtu}",
        "recommendation": rec
    }
