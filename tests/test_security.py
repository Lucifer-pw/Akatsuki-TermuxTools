"""Unit tests for Network Security & Protection Module"""
import unittest
from modules.net_security.arp_guard import ARPGuard
from modules.net_security.intruder_alert import add_to_whitelist, get_trusted_devices, remove_from_whitelist
from modules.net_security.nmap_scanner import python_probe_port, audit_router_security


class TestNetSecurity(unittest.TestCase):
    def test_arp_guard_init(self):
        guard = ARPGuard("127.0.0.1")
        self.assertEqual(guard.gateway_ip, "127.0.0.1")
        status = guard.check_arp_status()
        self.assertIn("status", status)

    def test_whitelist_management(self):
        test_mac = "aa:bb:cc:dd:ee:ff"
        # Add to whitelist
        self.assertTrue(add_to_whitelist(test_mac, "Test Device Mock", "192.168.1.99"))
        devices = get_trusted_devices()
        matched = any(d.get("mac") == test_mac for d in devices)
        self.assertTrue(matched)

        # Remove from whitelist
        self.assertTrue(remove_from_whitelist(test_mac))
        devices_after = get_trusted_devices()
        matched_after = any(d.get("mac") == test_mac for d in devices_after)
        self.assertFalse(matched_after)

    def test_router_security_audit(self):
        res = audit_router_security("127.0.0.1")
        self.assertIn("grade", res)
        self.assertIn("engine", res)
        self.assertIn("verdict", res)


if __name__ == "__main__":
    unittest.main()
