"""Unit tests for Router Automation Module"""
import unittest
from modules.router_control.manager import RouterManager
from modules.router_control.presets import ROUTER_PRESETS


class TestRouterControl(unittest.TestCase):
    def test_manager_init(self):
        rm = RouterManager(host="192.168.1.1")
        self.assertEqual(rm.host, "192.168.1.1")
        self.assertEqual(rm.username, "user")
        self.assertEqual(rm.password, "user1234")

    def test_presets_exist(self):
        self.assertGreaterEqual(len(ROUTER_PRESETS), 5)
        # Check ZTE preset
        zte_preset = next((p for p in ROUTER_PRESETS if p["driver"] == "zte"), None)
        self.assertIsNotNone(zte_preset)
        self.assertEqual(zte_preset["username"], "user")

    def test_driver_instantiation(self):
        rm = RouterManager(host="192.168.1.1")
        driver = rm.get_driver(model="zte")
        self.assertEqual(driver.host, "192.168.1.1")
        self.assertEqual(driver.username, "user")


if __name__ == "__main__":
    unittest.main()
