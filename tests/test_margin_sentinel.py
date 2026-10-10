"""POD Margin Sentinel - Comprehensive Unit Test Suite.

Zero-dependency Python unittest verifying financial calculations,
break-even solvers, platform fee matrix, and Antigravity MCP tools.
"""

import sys
import unittest
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pod_margin_sentinel.fee_structures import PLATFORM_FEES, CATALOG_BENCHMARKS
from pod_margin_sentinel.margin_engine import MarginEngine
from pod_margin_sentinel.mcp_server import handle_call_tool, TOOLS

class TestPODMarginSentinel(unittest.TestCase):
    """Rigorous unit test suite for POD Margin Sentinel."""

    def test_fee_structures_complete(self):
        """Verify all 5 core platform fee models are defined with valid parameters."""
        self.assertEqual(len(PLATFORM_FEES), 5)
        self.assertIn("etsy_organic", PLATFORM_FEES)
        self.assertIn("etsy_offsite_ads_15", PLATFORM_FEES)
        self.assertIn("etsy_offsite_ads_12", PLATFORM_FEES)
        self.assertIn("shopify_payments", PLATFORM_FEES)
        self.assertIn("tiktok_shop", PLATFORM_FEES)

        etsy = PLATFORM_FEES["etsy_organic"]
        self.assertEqual(etsy.transaction_percent, 0.065)
        self.assertEqual(etsy.payment_processing_percent, 0.030)
        self.assertEqual(etsy.payment_processing_fixed, 0.25)
        self.assertEqual(etsy.listing_fixed, 0.20)

    def test_calculate_order_profit_etsy_organic(self):
        """Test profit breakdown on standard Etsy organic sale (Gildan 18000 at $34.99)."""
        res = MarginEngine.calculate_order_profit(
            retail_price=34.99,
            wholesale_cost=12.50,
            factory_shipping=5.49,
            shipping_charged=0.0,
            platform_key="etsy_organic"
        )
        pricing = res["pricing"]
        cogs = res["cogs"]
        fees = res["fees_breakdown"]
        prof = res["profitability"]

        self.assertEqual(pricing["gross_revenue"], 34.99)
        self.assertEqual(cogs["total_cogs"], 17.99)
        self.assertAlmostEqual(fees["transaction_fee"], 2.27, places=2)
        self.assertAlmostEqual(fees["payment_processing"], 1.30, places=2)
        self.assertEqual(fees["listing_auto_renew"], 0.20)
        self.assertEqual(fees["offsite_ads_fee"], 0.0)

        # Net Profit = 34.99 - 3.77 - 17.99 = 13.23
        self.assertAlmostEqual(prof["net_dollar_profit"], 13.23, places=2)
        self.assertAlmostEqual(prof["net_margin_percent"], 37.81, places=1)
        self.assertEqual(prof["health_tier"], "HEALTHY")
        self.assertTrue(prof["is_profitable"])

    def test_calculate_order_profit_offsite_ads(self):
        """Test profit impact when Etsy 15% Offsite Ads triggers."""
        res = MarginEngine.calculate_order_profit(
            retail_price=34.99,
            wholesale_cost=12.50,
            factory_shipping=5.49,
            platform_key="etsy_offsite_ads_15"
        )
        fees = res["fees_breakdown"]
        prof = res["profitability"]

        # Offsite Ads 15% on $34.99 is $5.25
        self.assertAlmostEqual(fees["offsite_ads_fee"], 5.25, places=2)
        self.assertAlmostEqual(prof["net_dollar_profit"], 7.98, places=2)
        self.assertAlmostEqual(prof["net_margin_percent"], 22.81, places=1)

    def test_break_even_calculation(self):
        """Verify break-even price calculation results in ~0.00 net profit."""
        be_price = MarginEngine.calculate_break_even_price(
            wholesale_cost=12.50,
            factory_shipping=5.49,
            platform_key="etsy_organic"
        )
        self.assertGreater(be_price, 17.99)  # Must be greater than COGS

        # Verify running profit calculation at break-even price
        verification = MarginEngine.calculate_order_profit(
            retail_price=be_price,
            wholesale_cost=12.50,
            factory_shipping=5.49,
            platform_key="etsy_organic"
        )
        self.assertAlmostEqual(verification["profitability"]["net_dollar_profit"], 0.0, delta=0.08)

    def test_recommended_retail_price(self):
        """Verify target margin pricing reverse-solver achieves the exact desired percentage."""
        target_margin = 40.0
        rec_price = MarginEngine.recommend_retail_price(
            wholesale_cost=12.50,
            factory_shipping=5.49,
            target_margin_percent=target_margin,
            platform_key="etsy_organic"
        )
        self.assertGreater(rec_price, 25.0)

        verification = MarginEngine.calculate_order_profit(
            retail_price=rec_price,
            wholesale_cost=12.50,
            factory_shipping=5.49,
            platform_key="etsy_organic"
        )
        self.assertAlmostEqual(verification["profitability"]["net_margin_percent"], target_margin, delta=0.5)

    def test_coupon_safety_stress_test(self):
        """Verify coupon discount stress testing flags steep discounts."""
        stress = MarginEngine.evaluate_coupon_safety(
            retail_price=34.99,
            wholesale_cost=12.50,
            factory_shipping=5.49,
            platform_key="etsy_organic",
            min_acceptable_margin=15.0
        )
        self.assertIn("max_safe_coupon_percent", stress)
        scenarios = stress["discount_scenarios"]
        self.assertEqual(len(scenarios), 5)  # 10%, 15%, 20%, 25%, 30%

        # 10% coupon should be approved
        self.assertTrue(scenarios[0]["is_safe"])
        # 30% coupon should compress margin
        self.assertLess(scenarios[4]["net_margin_percent"], scenarios[0]["net_margin_percent"])

    def test_mcp_tools(self):
        """Verify all 6 MCP JSON-RPC tools execute properly."""
        self.assertEqual(len(TOOLS), 6)

        # 1. margin_calculate_order_profit
        t1 = handle_call_tool("margin_calculate_order_profit", {
            "retail_price": 29.99,
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79
        })
        self.assertEqual(t1["status"], "success")
        self.assertIn("profit_analysis", t1)

        # 2. margin_simulate_offsite_ads
        t2 = handle_call_tool("margin_simulate_offsite_ads", {
            "retail_price": 29.99,
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79
        })
        self.assertIn("organic", t2)
        self.assertIn("offsite_ads_15_tier", t2)

        # 3. margin_recommend_retail_price
        t3 = handle_call_tool("margin_recommend_retail_price", {
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79,
            "target_margin_percent": 30.0
        })
        self.assertEqual(t3["status"], "success")
        self.assertGreater(t3["recommended_retail_price"], 20.0)

        # 4. margin_compare_platforms
        t4 = handle_call_tool("margin_compare_platforms", {
            "retail_price": 29.99,
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79
        })
        self.assertEqual(len(t4["platforms"]), 5)

        # 5. margin_calculate_break_even
        t5 = handle_call_tool("margin_calculate_break_even", {
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79
        })
        self.assertEqual(t5["status"], "success")
        self.assertGreater(t5["break_even_retail_price"], 15.0)

        # 6. margin_evaluate_coupon_safety
        t6 = handle_call_tool("margin_evaluate_coupon_safety", {
            "retail_price": 29.99,
            "wholesale_cost": 10.80,
            "factory_shipping": 4.79
        })
        self.assertIn("coupon_safety", t6)

if __name__ == "__main__":
    unittest.main()
