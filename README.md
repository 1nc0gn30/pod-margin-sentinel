# POD Margin Sentinel

Exact per-order P&L for print-on-demand products across Etsy (organic and
Offsite Ads 15% / 12% tiers), Shopify Payments and TikTok Shop: platform fees,
COGS, net margin, break-even and target-margin pricing, and coupon safety.
Pure Python stdlib.

## Use

```bash
export PYTHONPATH=src
python3 -m pod_margin_sentinel.cli --help
python3 -m pod_margin_sentinel.cli coupon --retail 34.99 --wholesale 12.5 --shipping 5.49 --min-margin 15
```

`coupon` reports both the safest standard tier (10/15/20/25/30%) and the
**exact max safe discount** (0.1% resolution) that keeps net margin at or
above your floor, and warns when full price already misses it.

There's also a web UI/API (`server.py`) and an MCP stdio server (`mcp_server.py`).

## Fee model notes

- Etsy: 6.5% transaction on item + shipping, 3% + $0.25 Etsy Payments, $0.20 listing;
  Offsite Ads 15% (<$10k/yr) or 12%, **capped at $100 per order**.
- Shopify Payments Basic: 2.9% + $0.30. TikTok Shop US: 6% + $0.30.
- Verify current rates before relying on them; edit `fee_structures.py`.

Unknown platform keys, negative amounts, discounts outside 0-100% and
mathematically impossible target margins raise `ValueError` (the CLI prints a
clean `error:` line) instead of silently returning a guess.

## Test

```bash
python3 -m pytest -q tests/
```

## Network exposure

The server binds to `127.0.0.1` by default. To reach it from other devices,
opt in explicitly with `--host 0.0.0.0` (or set `ZOTH_BIND_HOST=0.0.0.0`; an IP
in `HOST` is also honoured, a plain hostname is ignored) and only on a trusted
network.

Browser requests are only accepted from `localhost` / `127.0.0.1` pages:
cross-site POSTs get `403` and CORS never answers `*`, so a website you visit
can't drive this local server. CLI and agent clients are unaffected.
