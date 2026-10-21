"""Network and Bandwidth Optimizer Module"""
from .dns_bench import run_dns_benchmark
from .ping_keeper import run_ping_keepalive
from .mtu_finder import find_optimal_mtu
from .lan_scanner import scan_local_network
from .bandwidth_monitor import run_bandwidth_monitor
from .ui import run_network_module

__all__ = ["run_dns_benchmark", "run_ping_keepalive", "find_optimal_mtu", "scan_local_network", "run_bandwidth_monitor", "run_network_module"]
