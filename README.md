<p align="center">
  <img src="assets/banner.png" alt="POD Margin Sentinel: Profit margin calculator, break-even solver, fee simulator, and MCP server" width="100%" />
</p>

# POD Margin Sentinel

Zero-dependency Python 3.10+ financial margin engine and fee calculator for print-on-demand sellers: marketplace fee simulation across Etsy, Shopify, and TikTok Shop, break-even price solving, coupon stress testing, wholesale catalog benchmarks, loopback HTTP workstation, and a 5-tool MCP stdio server.

- Zoth Studio v2 dossier: https://zoth.nullai.tech/tools/pod-margin-sentinel
- Local workstation: `http://127.0.0.1:8120`
- Runtime dependencies: none (Python standard library only)
- License: MIT

## What It Does

- **Multi-channel fee modeling**: Calculates granular transaction, gateway payment processing, listing, and marketing ad fees for:
  - `etsy_organic`: 6.5% transaction fee + 3.0% + $0.25 payment processing + $0.20 auto-renew listing fee.
  - `etsy_offsite_ads_15`: Standard 15% Etsy Offsite Ads fee tier.
  - `etsy_offsite_ads_12`: High-volume 12% Etsy Offsite Ads fee tier.
  - `shopify_payments`: 2.9% + $0.30 credit card gateway processing.
  - `tiktok_shop`: 6.0% commission + 2.9% payment processing.
- **Break-even solving**: Calculates exact retail price required to achieve $0.00 net profit after factoring in base manufacturing costs, supplier shipping, and marketplace percentages.
- **Target margin recommendations**: Solves for necessary retail price to guarantee specific margin floors (e.g., 30%, 40%, 50%, 65%).
- **Coupon stress testing**: Simulates profitability under standard discount promotions (10%, 15%, 20%, 25%, 30%) and calculates the exact maximum coupon percentage before margins breach an acceptable threshold.
- **Catalog benchmarks**: Bundled wholesale cost references for standard POD items (tees, hoodies, mugs, canvases, journals) across Printify and Gelato.

## How It Works

```text
src/pod_margin_sentinel/
├── fee_structures.py   # Fee schedules and catalog benchmarks
├── margin_engine.py    # Profitability calculations, break-even solver, coupon stress tester
├── mcp_server.py       # MCP stdio server (JSON-RPC 2.0: initialize, tools/list, tools/call)
├── server.py           # Loopback HTTP API + static workstation from public/
└── cli.py              # `pod-margin-sentinel` entry point
bin/pod-margin-sentinel      # Runs the CLI from checkout
public/                      # Browser workstation (calculator, comparison table, coupon matrix)
```

The HTTP server only accepts browser requests from `localhost` / `127.0.0.1` / `[::1]` origins and binds to `127.0.0.1` by default.

## Install

```bash
git clone https://github.com/1nc0gn30/pod-margin-sentinel.git
cd pod-margin-sentinel
pip install -e .
```

Or run directly without installation via the runner script:

```bash
./bin/pod-margin-sentinel --help
```

## Configuration

The core margin engine and benchmark lookup run completely offline with no API keys or environment variables required.

Optional environment variables:
- `MARGIN_SENTINEL_PORT`: Custom listening port for the HTTP daemon (default: `8120`).
- `ZOTH_BIND_HOST`: Custom bind interface (default: `127.0.0.1`).

## CLI reference

```bash
# Check service status and catalog benchmarks
pod-margin-sentinel status
pod-margin-sentinel --json

# Calculate order profit for a Bella+Canvas 3001 on Etsy
pod-margin-sentinel calc --retail 28.00 --wholesale 9.50 --shipping 4.99 --platform etsy_organic

# Compare net profits across all platforms side-by-side
pod-margin-sentinel compare --retail 28.00 --wholesale 9.50 --shipping 4.99

# Solve for break-even and 35% target margin price
pod-margin-sentinel breakeven --wholesale 9.50 --shipping 4.99 --target-margin 35.0

# Stress-test promotional coupons against a 15% minimum margin floor
pod-margin-sentinel coupon --retail 28.00 --wholesale 9.50 --shipping 4.99 --min-margin 15.0

# List catalog wholesale benchmarks
pod-margin-sentinel benchmarks

# Launch local HTTP workstation
pod-margin-sentinel server --port 8120

# Launch MCP stdio server
pod-margin-sentinel mcp
```

## MCP/REST reference

### MCP stdio tools

When registered in an MCP host (such as Antigravity or Claude Desktop):
- `calculate_order_profit`: Computes gross revenue, fee breakdown, COGS, net dollar profit, and net margin percentage.
- `compare_all_platforms`: Generates side-by-side comparison across Etsy, Shopify, and TikTok Shop.
- `calculate_break_even_price`: Solves for zero-dollar net profit price and target margin retail price.
- `evaluate_coupon_safety`: Tests discount tiers (10% to 30%) against a margin threshold.
- `list_catalog_benchmarks`: Returns wholesale benchmarks for standard POD items.

### REST endpoints

- `GET /health` - Service health and uptime.
- `GET /api/benchmarks` - List bundled catalog benchmarks.
- `GET /api/platforms` - Supported fee schedule names.
- `POST /api/calculate` - Order profit metrics JSON payload.
- `POST /api/compare` - Multi-channel comparison JSON payload.
- `POST /api/breakeven` - Break-even solver JSON payload.
- `POST /api/coupon` - Coupon evaluation JSON payload.

## Port

Default HTTP port: `8120`.

## License

MIT License. Engineered by [1nc0gn30](https://1nc0gn30.si) • [NullAI Platform](https://nullai.tech). 100% Free and Open-Source.
Optional tip link: [Buy Us a Coffee](https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X).
