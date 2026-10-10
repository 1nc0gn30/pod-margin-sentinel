"""POD Margin Sentinel - Antigravity MCP Server.

Implements 6 production JSON-RPC 2.0 tools for Print-on-Demand financial calculation,
break-even simulation, and fee optimization.
"""

import json
import sys
from typing import Dict, Any, List

from .fee_structures import PLATFORM_FEES, CATALOG_BENCHMARKS
from .margin_engine import MarginEngine

TOOLS = [
    {
        "name": "margin_calculate_order_profit",
        "description": "Calculate itemized transaction fees, payment processing, manufacturing COGS, net dollar profit, and net margin percentage for a POD order.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "retail_price": {"type": "number", "description": "Retail price charged to customer in USD"},
                "wholesale_cost": {"type": "number", "description": "Base production wholesale cost from Printify or Gelato in USD"},
                "factory_shipping": {"type": "number", "description": "Manufacturing partner shipping cost in USD"},
                "shipping_charged": {"type": "number", "description": "Shipping charged to customer in USD (0.0 for Free Shipping)", "default": 0.0},
                "platform_key": {
                    "type": "string",
                    "description": "Platform fee schedule",
                    "enum": ["etsy_organic", "etsy_offsite_ads_15", "etsy_offsite_ads_12", "shopify_payments", "tiktok_shop"],
                    "default": "etsy_organic"
                },
                "discount_percent": {"type": "number", "description": "Discount coupon percentage (0 to 100)", "default": 0.0}
            },
            "required": ["retail_price", "wholesale_cost", "factory_shipping"]
        }
    },
    {
        "name": "margin_simulate_offsite_ads",
        "description": "Simulate margin erosion across 0% (organic), 12% (established store), and 15% (standard store) Etsy Offsite Ads scenarios.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "retail_price": {"type": "number", "description": "Retail price in USD"},
                "wholesale_cost": {"type": "number", "description": "Wholesale manufacturing cost in USD"},
                "factory_shipping": {"type": "number", "description": "Factory shipping in USD"},
                "shipping_charged": {"type": "number", "description": "Shipping charged to customer in USD", "default": 0.0}
            },
            "required": ["retail_price", "wholesale_cost", "factory_shipping"]
        }
    },
    {
        "name": "margin_recommend_retail_price",
        "description": "Reverse-calculate the exact retail price required to achieve a target net profit margin (e.g. 35%, 45%, 50%).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wholesale_cost": {"type": "number", "description": "Base wholesale cost in USD"},
                "factory_shipping": {"type": "number", "description": "Factory shipping in USD"},
                "target_margin_percent": {"type": "number", "description": "Desired net margin percentage (e.g. 35.0)", "default": 35.0},
                "shipping_charged": {"type": "number", "description": "Shipping charged to customer in USD", "default": 0.0},
                "platform_key": {"type": "string", "default": "etsy_organic"}
            },
            "required": ["wholesale_cost", "factory_shipping"]
        }
    },
    {
        "name": "margin_compare_platforms",
        "description": "Compare net dollar profit and net margin percentage side-by-side across Etsy Organic, Etsy Ads, Shopify, and TikTok Shop.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "retail_price": {"type": "number", "description": "Retail price in USD"},
                "wholesale_cost": {"type": "number", "description": "Base wholesale cost in USD"},
                "factory_shipping": {"type": "number", "description": "Factory shipping in USD"},
                "shipping_charged": {"type": "number", "description": "Shipping charged to customer in USD", "default": 0.0}
            },
            "required": ["retail_price", "wholesale_cost", "factory_shipping"]
        }
    },
    {
        "name": "margin_calculate_break_even",
        "description": "Calculate absolute minimum retail price to break even ($0.00 profit) under current marketplace commission schedules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wholesale_cost": {"type": "number", "description": "Base wholesale cost in USD"},
                "factory_shipping": {"type": "number", "description": "Factory shipping in USD"},
                "shipping_charged": {"type": "number", "description": "Shipping charged to customer in USD", "default": 0.0},
                "platform_key": {"type": "string", "default": "etsy_organic"}
            },
            "required": ["wholesale_cost", "factory_shipping"]
        }
    },
    {
        "name": "margin_evaluate_coupon_safety",
        "description": "Stress-test discount coupons (10%, 15%, 20%, 25%, 30%) to ensure profit margins do not dip below minimum safe levels.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "retail_price": {"type": "number", "description": "Current retail price in USD"},
                "wholesale_cost": {"type": "number", "description": "Base wholesale cost in USD"},
                "factory_shipping": {"type": "number", "description": "Factory shipping in USD"},
                "shipping_charged": {"type": "number", "description": "Shipping charged in USD", "default": 0.0},
                "min_acceptable_margin": {"type": "number", "description": "Minimum acceptable net margin percentage", "default": 15.0}
            },
            "required": ["retail_price", "wholesale_cost", "factory_shipping"]
        }
    }
]

def handle_call_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "margin_calculate_order_profit":
        res = MarginEngine.calculate_order_profit(
            retail_price=args["retail_price"],
            wholesale_cost=args["wholesale_cost"],
            factory_shipping=args["factory_shipping"],
            shipping_charged=args.get("shipping_charged", 0.0),
            platform_key=args.get("platform_key", "etsy_organic"),
            discount_percent=args.get("discount_percent", 0.0)
        )
        return {"status": "success", "profit_analysis": res}

    elif name == "margin_simulate_offsite_ads":
        r = args["retail_price"]
        w = args["wholesale_cost"]
        fs = args["factory_shipping"]
        sc = args.get("shipping_charged", 0.0)

        organic = MarginEngine.calculate_order_profit(r, w, fs, sc, "etsy_organic")
        ads12 = MarginEngine.calculate_order_profit(r, w, fs, sc, "etsy_offsite_ads_12")
        ads15 = MarginEngine.calculate_order_profit(r, w, fs, sc, "etsy_offsite_ads_15")

        return {
            "status": "success",
            "organic": {
                "net_profit": organic["profitability"]["net_dollar_profit"],
                "net_margin": organic["profitability"]["net_margin_percent"]
            },
            "offsite_ads_12_tier": {
                "net_profit": ads12["profitability"]["net_dollar_profit"],
                "net_margin": ads12["profitability"]["net_margin_percent"],
                "profit_reduction": round(organic["profitability"]["net_dollar_profit"] - ads12["profitability"]["net_dollar_profit"], 2)
            },
            "offsite_ads_15_tier": {
                "net_profit": ads15["profitability"]["net_dollar_profit"],
                "net_margin": ads15["profitability"]["net_margin_percent"],
                "profit_reduction": round(organic["profitability"]["net_dollar_profit"] - ads15["profitability"]["net_dollar_profit"], 2)
            }
        }

    elif name == "margin_recommend_retail_price":
        w = args["wholesale_cost"]
        fs = args["factory_shipping"]
        target = args.get("target_margin_percent", 35.0)
        sc = args.get("shipping_charged", 0.0)
        pk = args.get("platform_key", "etsy_organic")

        price = MarginEngine.recommend_retail_price(w, fs, target, sc, pk)
        verification = MarginEngine.calculate_order_profit(price, w, fs, sc, pk)

        return {
            "status": "success",
            "target_margin_percent": target,
            "recommended_retail_price": price,
            "verified_net_profit": verification["profitability"]["net_dollar_profit"],
            "verified_net_margin_percent": verification["profitability"]["net_margin_percent"]
        }

    elif name == "margin_compare_platforms":
        res = MarginEngine.compare_all_platforms(
            retail_price=args["retail_price"],
            wholesale_cost=args["wholesale_cost"],
            factory_shipping=args["factory_shipping"],
            shipping_charged=args.get("shipping_charged", 0.0)
        )
        return {"status": "success", "platforms": res}

    elif name == "margin_calculate_break_even":
        w = args["wholesale_cost"]
        fs = args["factory_shipping"]
        sc = args.get("shipping_charged", 0.0)
        pk = args.get("platform_key", "etsy_organic")

        be = MarginEngine.calculate_break_even_price(w, fs, sc, pk)
        return {
            "status": "success",
            "break_even_retail_price": be,
            "platform_key": pk
        }

    elif name == "margin_evaluate_coupon_safety":
        res = MarginEngine.evaluate_coupon_safety(
            retail_price=args["retail_price"],
            wholesale_cost=args["wholesale_cost"],
            factory_shipping=args["factory_shipping"],
            shipping_charged=args.get("shipping_charged", 0.0),
            min_acceptable_margin=args.get("min_acceptable_margin", 15.0)
        )
        return {"status": "success", "coupon_safety": res}

    raise ValueError(f"Unknown tool: {name}")

def run_mcp():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                params = req.get("params", {})
                t_name = params.get("name")
                t_args = params.get("arguments", {})
                res = handle_call_tool(t_name, t_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            elif method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "pod-margin-sentinel", "version": "1.0.0"}
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": req.get("id") if "req" in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_mcp()
