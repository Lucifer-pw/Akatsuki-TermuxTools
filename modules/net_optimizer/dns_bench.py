"""
Multi-DNS Latency Benchmark & Optimizer
Measures DNS query resolution speed (ms) across major public and local DNS servers.
"""
import time
from typing import List, Dict, Any, Optional
import dns.resolver

DNS_TARGETS = [
    {"name": "Cloudflare DNS (Primary)", "ip": "1.1.1.1", "doh": "1dot1dot1dot1.cloudflare-dns.com"},
    {"name": "Cloudflare DNS (Secondary)", "ip": "1.0.0.1", "doh": "1dot1dot1dot1.cloudflare-dns.com"},
    {"name": "Google Public DNS (Primary)", "ip": "8.8.8.8", "doh": "dns.google"},
    {"name": "Google Public DNS (Secondary)", "ip": "8.8.4.4", "doh": "dns.google"},
    {"name": "Quad9 Privacy & Security", "ip": "9.9.9.9", "doh": "dns.quad9.net"},
    {"name": "AdGuard DNS (Ad-Blocking)", "ip": "94.140.14.14", "doh": "dns.adguard-dns.com"},
    {"name": "OpenDNS Home", "ip": "208.67.222.222", "doh": "dns.opendns.com"}
]

TEST_DOMAINS = ["google.com", "cloudflare.com", "wikipedia.org", "github.com"]


def benchmark_single_dns(server_ip: str, rounds: int = 3) -> Dict[str, Any]:
    """
    Measures resolution latency for a specific DNS nameserver across test domains.
    Returns statistics dict with min, max, avg latencies.
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.timeout = 2.0
    resolver.lifetime = 2.0

    latencies: List[float] = []
    failed_queries = 0

    for domain in TEST_DOMAINS[:rounds]:
        try:
            start_time = time.perf_counter()
            resolver.resolve(domain, "A")
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            latencies.append(elapsed_ms)
        except Exception:
            failed_queries += 1

    if not latencies:
        return {
            "success": False,
            "avg_ms": 9999.0,
            "min_ms": 9999.0,
            "max_ms": 9999.0,
            "loss_pct": 100.0
        }

    return {
        "success": True,
        "avg_ms": round(sum(latencies) / len(latencies), 1),
        "min_ms": round(min(latencies), 1),
        "max_ms": round(max(latencies), 1),
        "loss_pct": round((failed_queries / (len(latencies) + failed_queries)) * 100, 1)
    }


def run_dns_benchmark(gateway_ip: Optional[str] = None, rounds: int = 3) -> List[Dict[str, Any]]:
    """
    Runs benchmark on all candidate DNS servers plus local gateway DNS.
    Returns results sorted by lowest average latency.
    """
    candidates = list(DNS_TARGETS)
    if gateway_ip:
        candidates.insert(0, {
            "name": f"Local Gateway / ISP DNS ({gateway_ip})",
            "ip": gateway_ip,
            "doh": "Local Router"
        })

    results = []
    for item in candidates:
        stats = benchmark_single_dns(item["ip"], rounds=rounds)
        results.append({
            "name": item["name"],
            "ip": item["ip"],
            "doh": item.get("doh", "-"),
            **stats
        })

    # Sort: reachable first by avg_ms, then unreachable
    results.sort(key=lambda x: (not x["success"], x["avg_ms"]))
    return results
