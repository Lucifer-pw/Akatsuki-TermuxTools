"""
Nmap Security Auditor & Port Scanner Wrapper
Dual-Engine:
- Uses native 'nmap' binary if installed on Termux / Windows.
- Pure Python multi-threaded fallback scanner if Nmap is not installed.
Specialized in local router vulnerability auditing and device service mapping.
"""
import sys
import shutil
import socket
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple
from core.utils import get_default_gateway

# High-risk security port database
PORT_RISK_DB = {
    21: ("FTP", "Medium", "File transfer tanpa enkripsi."),
    22: ("SSH", "Low", "Akses remote shell terenkripsi."),
    23: ("Telnet", "CRITICAL", "Akses remote tidak terenkripsi! Celah utama botnet router."),
    25: ("SMTP", "Medium", "Mail transfer port."),
    53: ("DNS", "Low", "Domain name resolution."),
    80: ("HTTP", "Low", "Web management portal."),
    135: ("MSRPC", "Medium", "Microsoft RPC endpoint."),
    139: ("NetBIOS", "Medium", "NetBIOS file sharing."),
    443: ("HTTPS", "Low", "Secure web management."),
    445: ("SMB", "High", "Windows file sharing (rentan EternalBlue/WannaCry)."),
    554: ("RTSP", "Low", "Video streaming / CCTV stream."),
    1900: ("UPnP SSDP", "High", "Universal Plug and Play. Potensi eksploitasi WAN/LAN."),
    3389: ("RDP", "High", "Remote Desktop Protocol."),
    5000: ("UPnP / AirPlay", "Medium", "UPnP control point."),
    5228: ("Google Play", "Low", "Android push notification."),
    7547: ("TR-069 CWMP", "High", "Port manajemen jarak jauh ISP. Sering diserang botnet."),
    8080: ("HTTP-Alt", "Low", "Web management alternatif."),
    8443: ("HTTPS-Alt", "Low", "Secure web management alternatif."),
    49152: ("UPnP Service", "Medium", "WPS device management / UPnP service.")
}


def is_nmap_installed() -> bool:
    """Checks whether the 'nmap' executable exists on PATH."""
    return shutil.which("nmap") is not None


def python_probe_port(ip: str, port: int, timeout: float = 0.3) -> Optional[Dict[str, Any]]:
    """Probes a single port using pure Python sockets."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((ip, port))
        if res == 0:
            # Grab banner if possible
            banner = ""
            try:
                s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                raw = s.recv(256).decode("latin1", errors="ignore")
                for line in raw.split("\r\n"):
                    if "server:" in line.lower():
                        banner = line.split(":", 1)[1].strip()
                        break
            except Exception:
                pass
            s.close()

            risk_info = PORT_RISK_DB.get(port, ("Custom", "Low", "Layanan aplikasi standar"))
            return {
                "port": port,
                "protocol": "tcp",
                "state": "open",
                "service": risk_info[0],
                "risk_level": risk_info[1],
                "description": risk_info[2],
                "version": banner or "Layanan Aktif"
            }
        s.close()
    except Exception:
        s.close()
    return None


def run_python_fallback_scan(ip: str, ports: List[int]) -> List[Dict[str, Any]]:
    """Pure Python multi-threaded port scanner."""
    results = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(python_probe_port, ip, p) for p in ports]
        for f in futures:
            item = f.result()
            if item:
                results.append(item)
    results.sort(key=lambda x: x["port"])
    return results


def run_nmap_native_scan(ip: str, ports_arg: str = "21-23,25,53,80,135,139,443,445,1900,3389,7547,8080,8443,49152") -> List[Dict[str, Any]]:
    """Executes native nmap binary with version detection (-sV)."""
    cmd = ["nmap", "-sV", "-T4", "-p", ports_arg, ip]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = proc.stdout

        results = []
        # Parse nmap output:
        # PORT     STATE SERVICE VERSION
        # 80/tcp   open  http    nginx
        for line in out.splitlines():
            match = re.search(r"^(\d+)/(tcp|udp)\s+(\w+)\s+([^\s]+)\s*(.*)?$", line.strip())
            if match:
                port = int(match.group(1))
                proto = match.group(2)
                state = match.group(3)
                service = match.group(4)
                version = match.group(5) or service

                if state == "open":
                    risk_info = PORT_RISK_DB.get(port, (service, "Low", "Layanan aplikasi standar"))
                    results.append({
                        "port": port,
                        "protocol": proto,
                        "state": state,
                        "service": service,
                        "risk_level": risk_info[1],
                        "description": risk_info[2],
                        "version": version.strip()
                    })
        return results
    except Exception:
        # Fall back to pure Python if nmap execution failed
        return []


def audit_router_security(gateway_ip: Optional[str] = None) -> Dict[str, Any]:
    """
    Audits local gateway router for exposed management services and vulnerability risks.
    """
    target = gateway_ip or get_default_gateway()
    audit_ports = [21, 22, 23, 53, 80, 443, 1900, 5000, 7547, 8080, 8443, 49152]

    engine_used = "Native Nmap" if is_nmap_installed() else "Pure Python Fallback"

    if is_nmap_installed():
        ports_str = ",".join(map(str, audit_ports))
        open_ports = run_nmap_native_scan(target, ports_str)
        if not open_ports:
            open_ports = run_python_fallback_scan(target, audit_ports)
    else:
        open_ports = run_python_fallback_scan(target, audit_ports)

    # Determine security score & findings
    has_critical = any(p["risk_level"] == "CRITICAL" for p in open_ports)
    has_high = any(p["risk_level"] == "High" for p in open_ports)

    if has_critical:
        grade = "D (Berisiko Tinggi)"
        verdict = "DITEMUKAN CELAH KRITIS! Port berbahaya (seperti Telnet 23) terbuka tanpa proteksi."
    elif has_high:
        grade = "B- (Perlu Perhatian)"
        verdict = "Port berisiko (UPnP / TR-069 / SMB) terdeteksi terbuka. Disarankan ditinjau di web router."
    elif len(open_ports) > 0:
        grade = "A (Aman)"
        verdict = "Hanya port manajemen standar (Web HTTP/HTTPS) yang terbuka."
    else:
        grade = "A+ (Sangat Aman)"
        verdict = "Tidak ada port sensitif yang terbuka ke jaringan lokal."

    return {
        "target": target,
        "engine": engine_used,
        "grade": grade,
        "verdict": verdict,
        "open_services": open_ports
    }
