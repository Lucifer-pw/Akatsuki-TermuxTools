"""Unit tests for Network & Bandwidth Optimizer Module"""
import unittest
from modules.net_optimizer.dns_bench import benchmark_single_dns
from modules.net_optimizer.mtu_finder import find_optimal_mtu
from modules.net_optimizer.bandwidth_monitor import classify_activity, estimate_bandwidth_score


class TestNetOptimizer(unittest.TestCase):
    def test_dns_benchmark_cloudflare(self):
        res = benchmark_single_dns("1.1.1.1", rounds=1)
        self.assertIn("success", res)
        self.assertIn("avg_ms", res)
        self.assertTrue(res["success"])
        self.assertLess(res["avg_ms"], 2000.0)

    def test_mtu_finder(self):
        res = find_optimal_mtu("1.1.1.1")
        self.assertIn("optimal_mtu", res)
        self.assertGreaterEqual(res["optimal_mtu"], 1300)
        self.assertLessEqual(res["optimal_mtu"], 1500)

    def test_bandwidth_classification(self):
        act, cat = classify_activity([80, 443])
        self.assertEqual(cat, "browsing")
        act_tor, cat_tor = classify_activity([6881])
        self.assertEqual(cat_tor, "download")
        score, badge = estimate_bandwidth_score(25.0, [6881])
        self.assertGreaterEqual(score, 50)


if __name__ == "__main__":
    unittest.main()
