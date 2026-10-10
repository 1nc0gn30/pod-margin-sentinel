"""POD Margin Sentinel - Sovereign Command-Line Interface.

Zero-dependency Python 3.10+ Standard Library CLI.
"""

import argparse
import json
import sys

from .fee_structures import PLATFORM_FEES, CATALOG_BENCHMARKS, get_benchmarks_list
from .margin_engine import MarginEngine
from .server import run_server
from .mcp_server import run_mcp

def main():
    parser = argparse.ArgumentParser(
        prog="pod-margin-sentinel",
        description="Autonomous POD Profit Sentinel & Break-Even Matrix across Etsy, Shopify, and TikTok Shop"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: calc
    p_calc = subparsers.add_parser("calc", help="Calculate granular profit metrics for a POD order")
    p_calc.add_argument("--retail", type=float, required=True, help="Retail price charged to customer in USD")
    p_calc.add_argument("--wholesale", type=float, required=True, help="Base manufacturing wholesale cost in USD")
    p_calc.add_argument("--shipping", type=float, required=True, help="Factory shipping cost in USD")
    p_calc.add_argument("--charged-shipping", type=float, default=0.0, help="Shipping charged to customer (0 for free shipping)")
    p_calc.add_argument("--platform", default="etsy_organic", choices=list(PLATFORM_FEES.keys()), help="Platform fee schedule")
    p_calc.add_argument("--discount", type=float, default=0.0, help="Coupon discount percentage (0 to 100)")
    p_calc.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: compare
    p_comp = subparsers.add_parser("compare", help="Compare net profit across all marketplaces side-by-side")
    p_comp.add_argument("--retail", type=float, required=True, help="Retail price in USD")
    p_comp.add_argument("--wholesale", type=float, required=True, help="Wholesale cost in USD")
    p_comp.add_argument("--shipping", type=float, required=True, help="Factory shipping in USD")
    p_comp.add_argument("--charged-shipping", type=float, default=0.0, help="Customer shipping charged")
    p_comp.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: breakeven
    p_be = subparsers.add_parser("breakeven", help="Solve for break-even and target margin retail prices")
    p_be.add_argument("--wholesale", type=float, required=True, help="Wholesale cost in USD")
    p_be.add_argument("--shipping", type=float, required=True, help="Factory shipping in USD")
    p_be.add_argument("--target-margin", type=float, default=35.0, help="Target net margin percentage (e.g. 35.0)")
    p_be.add_argument("--platform", default="etsy_organic", choices=list(PLATFORM_FEES.keys()))
    p_be.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: coupon
    p_coup = subparsers.add_parser("coupon", help="Stress-test standard coupon discounts (10%-30%) for margin safety")
    p_coup.add_argument("--retail", type=float, required=True, help="Current retail price in USD")
    p_coup.add_argument("--wholesale", type=float, required=True, help="Wholesale cost in USD")
    p_coup.add_argument("--shipping", type=float, required=True, help="Factory shipping in USD")
    p_coup.add_argument("--min-margin", type=float, default=15.0, help="Minimum acceptable net margin percentage")
    p_coup.add_argument("--platform", default="etsy_organic", choices=list(PLATFORM_FEES.keys()))
    p_coup.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: benchmarks
    p_bm = subparsers.add_parser("benchmarks", help="List standard POD catalog wholesale benchmark costs")
    p_bm.add_argument("--json", action="store_true", help="Output raw JSON")

    # Command: server
    p_srv = subparsers.add_parser("server", help="Launch HTTP server and Web UI on port 8120")
    p_srv.add_argument("--port", type=int, default=8120, help="Port (default: 8120)")

    # Command: mcp
    p_mcp = subparsers.add_parser("mcp", help="Launch Antigravity MCP stdio server")

    args = parser.parse_args()

    if args.command == "calc":
        res = MarginEngine.calculate_order_profit(
            retail_price=args.retail,
            wholesale_cost=args.wholesale,
            factory_shipping=args.shipping,
            shipping_charged=args.charged_shipping,
            platform_key=args.platform,
            discount_percent=args.discount
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            p = res["profitability"]
            f = res["fees_breakdown"]
            c = res["cogs"]
            print("=" * 65)
            print(f"💰 POD MARGIN ANALYSIS: {res['platform'].upper()}")
            print("=" * 65)
            print(f"Gross Revenue:       ${res['pricing']['gross_revenue']:.2f}")
            print(f"Total COGS:          ${c['total_cogs']:.2f} (Base ${c['wholesale_base']:.2f} + Ship ${c['factory_shipping']:.2f})")
            print(f"Total Platform Fees: ${f['total_fees']:.2f} (Tx: ${f['transaction_fee']:.2f}, Gateway: ${f['payment_processing']:.2f}, Offsite: ${f['offsite_ads_fee']:.2f})")
            print("-" * 65)
            print(f"NET PROFIT:          ${p['net_dollar_profit']:.2f}")
            print(f"NET MARGIN:          {p['net_margin_percent']:.2f}%")
            print(f"Markup Multiplier:   {p['markup_multiplier']:.2f}x")
            print(f"Health Status:       {p['health_label']}")
            print("=" * 65)

    elif args.command == "compare":
        res = MarginEngine.compare_all_platforms(
            retail_price=args.retail,
            wholesale_cost=args.wholesale,
            factory_shipping=args.shipping,
            shipping_charged=args.charged_shipping
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("=" * 75)
            print(f"POD PLATFORM PROFIT COMPARISON (Retail: ${args.retail:.2f} | COGS: ${args.wholesale + args.shipping:.2f})")
            print("=" * 75)
            for row in res:
                print(f"• {row['platform_name']}")
                print(f"  Revenue: ${row['gross_revenue']:.2f} | Fees: ${row['total_fees']:.2f} | Net Profit: ${row['net_profit']:.2f} ({row['net_margin_percent']:.1f}%)")
                print("-" * 75)

    elif args.command == "breakeven":
        be = MarginEngine.calculate_break_even_price(
            args.wholesale, args.shipping, platform_key=args.platform
        )
        rec = MarginEngine.recommend_retail_price(
            args.wholesale, args.shipping, target_margin_percent=args.target_margin, platform_key=args.platform
        )
        if args.json:
            print(json.dumps({
                "wholesale": args.wholesale,
                "shipping": args.shipping,
                "break_even_price": be,
                "target_margin": args.target_margin,
                "recommended_price": rec,
                "platform": args.platform
            }, indent=2))
        else:
            cogs = args.wholesale + args.shipping
            print("=" * 65)
            print(f"🎯 BREAK-EVEN & TARGET PRICING ({args.platform})")
            print(f"Total Manufacturing COGS: ${cogs:.2f}")
            print(f"Break-Even Price ($0.00 Net): ${be:.2f}")
            print(f"Recommended Retail for {args.target_margin}% Margin: ${rec:.2f}")
            print("=" * 65)

    elif args.command == "coupon":
        res = MarginEngine.evaluate_coupon_safety(
            args.retail, args.wholesale, args.shipping,
            platform_key=args.platform, min_acceptable_margin=args.min_margin
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("=" * 70)
            print(f"COUPON DISCOUNT STRESS TEST (Retail: ${args.retail:.2f} | Min Safe Margin: {args.min_margin}%)")
            print(f"Maximum Safe Coupon: {res['max_safe_coupon_percent']:.0f}% OFF")
            print("=" * 70)
            for d in res["discount_scenarios"]:
                icon = "✓" if d["is_safe"] else "✗"
                print(f"  [{icon}] {d['discount_percent']:.0f}% Coupon → Price: ${d['discounted_price']:.2f} | Profit: ${d['net_profit']:.2f} ({d['net_margin_percent']:.1f}%) [{d['status']}]")
            print("=" * 70)

    elif args.command == "benchmarks":
        bm = get_benchmarks_list()
        if args.json:
            print(json.dumps(bm, indent=2))
        else:
            print("=" * 75)
            print("STANDARD POD CATALOG WHOLESALE BENCHMARKS")
            print("=" * 75)
            for b in bm:
                print(f"[{b['sku']}] {b['title']} ({b['category']})")
                print(f"  MSRP: ${b['recommended_retail']:.2f} | Printify Base: ${b['printify_base_cost']:.2f} + Ship ${b['printify_shipping']:.2f}")
                print(f"  Gelato Base: ${b['gelato_base_cost']:.2f} + Ship ${b['gelato_shipping']:.2f}")
                print("-" * 75)

    elif args.command == "server":
        run_server(args.port)

    elif args.command == "mcp":
        run_mcp()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
