"""POD Margin Sentinel - High-Performance Threaded HTTP Server (Port 8120).

Zero-dependency Python 3.10+ Standard Library HTTP & Static Server.
"""

import http.server
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, Any

from .fee_structures import PLATFORM_FEES, CATALOG_BENCHMARKS, get_benchmarks_list
from .margin_engine import MarginEngine

PORT = int(os.environ.get("MARGIN_SENTINEL_PORT", 8120))
START_TIME = time.time()

TELEMETRY = {
    "calculations_performed": 0,
    "break_evens_solved": 0,
    "platform_comparisons": 0,
    "coupon_stress_tests": 0
}

PUBLIC_DIR = Path(__file__).resolve().parent.parent.parent / "public"

class MarginSentinelHandler(http.server.SimpleHTTPRequestHandler):
    """Zero-dependency HTTP Handler for POD Margin Sentinel API and Web UI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._send_json({
                "status": "healthy",
                "service": "pod-margin-sentinel",
                "version": "1.0.0",
                "port": PORT,
                "uptime_seconds": round(time.time() - START_TIME, 1)
            })
            return

        if path == "/api/stats":
            self._send_json({
                "telemetry": TELEMETRY,
                "uptime_seconds": round(time.time() - START_TIME, 1)
            })
            return

        if path == "/api/benchmarks":
            self._send_json({
                "count": len(CATALOG_BENCHMARKS),
                "benchmarks": get_benchmarks_list()
            })
            return

        # Fallback to static web assets
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)
            payload = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception as e:
            self._send_json({"error": f"Invalid JSON payload: {str(e)}"}, status=400)
            return

        if path == "/api/calculate":
            retail = float(payload.get("retail_price", 34.99))
            wholesale = float(payload.get("wholesale_cost", 12.50))
            factory_ship = float(payload.get("factory_shipping", 5.49))
            charged_ship = float(payload.get("shipping_charged", 0.0))
            platform = payload.get("platform_key", "etsy_organic")
            discount = float(payload.get("discount_percent", 0.0))
            ad_spend = float(payload.get("ad_spend_per_order", 0.0))

            res = MarginEngine.calculate_order_profit(
                retail_price=retail,
                wholesale_cost=wholesale,
                factory_shipping=factory_ship,
                shipping_charged=charged_ship,
                platform_key=platform,
                discount_percent=discount,
                ad_spend_per_order=ad_spend
            )
            TELEMETRY["calculations_performed"] += 1
            self._send_json({"profit_analysis": res, "status": "success"})
            return

        if path == "/api/compare":
            retail = float(payload.get("retail_price", 34.99))
            wholesale = float(payload.get("wholesale_cost", 12.50))
            factory_ship = float(payload.get("factory_shipping", 5.49))
            charged_ship = float(payload.get("shipping_charged", 0.0))

            comparison = MarginEngine.compare_all_platforms(
                retail_price=retail,
                wholesale_cost=wholesale,
                factory_shipping=factory_ship,
                shipping_charged=charged_ship
            )
            TELEMETRY["platform_comparisons"] += 1
            self._send_json({"platforms": comparison, "status": "success"})
            return

        if path == "/api/break_even":
            wholesale = float(payload.get("wholesale_cost", 12.50))
            factory_ship = float(payload.get("factory_shipping", 5.49))
            charged_ship = float(payload.get("shipping_charged", 0.0))
            platform = payload.get("platform_key", "etsy_organic")
            target_margin = float(payload.get("target_margin_percent", 35.0))

            be_price = MarginEngine.calculate_break_even_price(
                wholesale_cost=wholesale,
                factory_shipping=factory_ship,
                shipping_charged=charged_ship,
                platform_key=platform
            )
            rec_price = MarginEngine.recommend_retail_price(
                wholesale_cost=wholesale,
                factory_shipping=factory_ship,
                target_margin_percent=target_margin,
                shipping_charged=charged_ship,
                platform_key=platform
            )
            TELEMETRY["break_evens_solved"] += 1
            self._send_json({
                "break_even_retail_price": be_price,
                "recommended_retail_price": rec_price,
                "target_margin_percent": target_margin,
                "status": "success"
            })
            return

        if path == "/api/coupon_stress":
            retail = float(payload.get("retail_price", 34.99))
            wholesale = float(payload.get("wholesale_cost", 12.50))
            factory_ship = float(payload.get("factory_shipping", 5.49))
            charged_ship = float(payload.get("shipping_charged", 0.0))
            platform = payload.get("platform_key", "etsy_organic")
            min_margin = float(payload.get("min_acceptable_margin", 15.0))

            evals = MarginEngine.evaluate_coupon_safety(
                retail_price=retail,
                wholesale_cost=wholesale,
                factory_shipping=factory_ship,
                shipping_charged=charged_ship,
                platform_key=platform,
                min_acceptable_margin=min_margin
            )
            TELEMETRY["coupon_stress_tests"] += 1
            self._send_json({"coupon_analysis": evals, "status": "success"})
            return

        self._send_json({"error": f"Endpoint not found: {path}"}, status=404)

def run_server(port: int = PORT):
    server_address = ("0.0.0.0", port)
    httpd = http.server.ThreadingHTTPServer(server_address, MarginSentinelHandler)
    print(f"🚀 POD Margin Sentinel listening on http://0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down POD Margin Sentinel gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
