"""Money-math invariants for POD Margin Sentinel (stdlib unittest, pytest-compatible)."""
import os, sys, unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from pod_margin_sentinel.fee_structures import PLATFORM_FEES, CATALOG_BENCHMARKS
from pod_margin_sentinel.margin_engine import MarginEngine as M


class TestMarginMath(unittest.TestCase):
    def test_unknown_platform_raises(self):
        for fn in (lambda: M.calculate_order_profit(30, 10, 5, platform_key="shopify"),
                   lambda: M.calculate_break_even_price(10, 5, platform_key="etsy"),
                   lambda: M.recommend_retail_price(10, 5, platform_key="amazon")):
            with self.assertRaises(ValueError):
                fn()

    def test_rejects_negative_and_bad_discount(self):
        with self.assertRaises(ValueError):
            M.calculate_order_profit(-1, 10, 5)
        with self.assertRaises(ValueError):
            M.calculate_order_profit(30, 10, 5, discount_percent=120)

    def test_profit_identity_all_platforms(self):
        for k in PLATFORM_FEES:
            r = M.calculate_order_profit(34.99, 12.5, 5.49, shipping_charged=3.0, platform_key=k)
            gross = r["pricing"]["gross_revenue"]
            self.assertAlmostEqual(r["profitability"]["net_dollar_profit"],
                                   gross - r["fees_breakdown"]["total_fees"] - r["cogs"]["total_cogs"], places=2)

    def test_break_even_is_zero_profit(self):
        for k in PLATFORM_FEES:
            for sku, b in CATALOG_BENCHMARKS.items():
                if b["printify_base_cost"] == 0:
                    continue
                be = M.calculate_break_even_price(b["printify_base_cost"], b["printify_shipping"], platform_key=k)
                p = M.calculate_order_profit(be, b["printify_base_cost"], b["printify_shipping"], platform_key=k)
                self.assertLessEqual(abs(p["profitability"]["net_dollar_profit"]), 0.03, (k, sku))

    def test_recommended_price_hits_target(self):
        for k in PLATFORM_FEES:
            price = M.recommend_retail_price(12.5, 5.49, target_margin_percent=35, platform_key=k)
            got = M.calculate_order_profit(price, 12.5, 5.49, platform_key=k)["profitability"]["net_margin_percent"]
            self.assertAlmostEqual(got, 35.0, delta=0.15, msg=k)

    def test_impossible_margin_raises_not_guess(self):
        with self.assertRaises(ValueError) as cm:
            M.recommend_retail_price(10, 5, target_margin_percent=95, platform_key="etsy_offsite_ads_15")
        self.assertIn("impossible", str(cm.exception))

    def test_offsite_ads_fee_capped_at_100(self):
        r = M.calculate_order_profit(2000, 300, 20, platform_key="etsy_offsite_ads_15")
        self.assertEqual(r["fees_breakdown"]["offsite_ads_fee"], 100.0)
        small = M.calculate_order_profit(30, 10, 5, platform_key="etsy_offsite_ads_15")
        self.assertAlmostEqual(small["fees_breakdown"]["offsite_ads_fee"], 4.5, places=2)

    def test_exact_max_safe_discount(self):
        d = M.max_safe_discount_percent(34.99, 12.5, 5.49, min_acceptable_margin=15)
        at = M.calculate_order_profit(34.99, 12.5, 5.49, discount_percent=d)["profitability"]["net_margin_percent"]
        over = M.calculate_order_profit(34.99, 12.5, 5.49, discount_percent=d + 0.5)["profitability"]["net_margin_percent"]
        self.assertGreaterEqual(at, 15.0)
        self.assertLess(over, 15.0)
        res = M.evaluate_coupon_safety(34.99, 12.5, 5.49, min_acceptable_margin=15)
        self.assertGreaterEqual(res["exact_max_safe_discount_percent"], res["max_safe_coupon_percent"])
        self.assertTrue(res["base_price_is_safe"])

    def test_unprofitable_base_reports_zero_and_unsafe(self):
        res = M.evaluate_coupon_safety(12.0, 10, 5, min_acceptable_margin=15)
        self.assertEqual(res["exact_max_safe_discount_percent"], 0.0)
        self.assertFalse(res["base_price_is_safe"])


if __name__ == "__main__":
    unittest.main()


class TestCliHelp(unittest.TestCase):
    def test_help_renders_for_all_commands(self):
        import subprocess
        env = dict(os.environ, PYTHONPATH=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
        p = subprocess.run([sys.executable, "-m", "pod_margin_sentinel.cli", "--help"], capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
