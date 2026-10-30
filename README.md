<div align="center">
  <img src="assets/banner.png" alt="POD Margin Sentinel — Sovereign Architecture Banner" width="100%" />
</div>

<br />

<div align="center">
  <a href="https://zoth.nullai.tech/tools/pod-margin-sentinel"><img src="https://img.shields.io/badge/Zoth_Studio_v2-Workspace-D4AF37?style=for-the-badge&logo=sparkles&logoColor=black" alt="Zoth Studio Workspace" /></a>
  <a href="http://127.0.0.1:8120"><img src="https://img.shields.io/badge/ZothOS_v3.3-Port_:8120-38BDF8?style=for-the-badge&logo=linux&logoColor=black" alt="Port :8120" /></a>
  <a href="https://nullai.tech"><img src="https://img.shields.io/badge/Security-100%25_Zero--Egress-10B981?style=for-the-badge&logo=shield&logoColor=black" alt="Zero Egress" /></a>
  <a href="https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X"><img src="https://img.shields.io/badge/☕_Buy_Us_a_Coffee-Stripe-D4AF37?style=for-the-badge" alt="Buy Us a Coffee" /></a>
</div>

# ⚡ POD Margin Sentinel (v2.5.0)

> **Autonomous real-time profit sentinel, break-even solver, and 2026 fee simulator across Etsy (Organic & 15% Ads), Shopify, and TikTok Shop.**

---

## 🏛️ Architectural Overview

**POD Margin Sentinel** is a financial defense and margin engineering workstation in the **[Zoth Studio v2](https://zoth.nullai.tech)** arsenal and **[ZothOS Linux 3.3](https://zothos.nullai.tech)** ecosystem, engineered by **Neal Frazier Tech ([@1nc0gn30](https://github.com/1nc0gn30))**.

| Property | Specification |
| :--- | :--- |
| **Tool ID** | `pod-margin-sentinel` |
| **Category** | `Commerce & MCP` |
| **Local Port** | `http://127.0.0.1:8120` |
| **Execution Mode** | Native Python Daemon & Browser Client |
| **Zoth Studio Route** | `http://127.0.0.1:3000/tools/pod-margin-sentinel` |
| **License** | 100% Free & Open Access (Zero Paywalls) |

---

## 💎 What It Does & How It Works

- **2026 Marketplace Fee Dissection**: Models complex hidden merchant fee waterfalls across all major POD sales channels:
  - `etsy_organic`: 6.5% transaction fee + 3.0% + $0.25 payment processing + $0.20 auto-renew listing fee.
  - `etsy_offsite_ads_15`: Adds mandatory 15% Offsite Ads tariff for shops under $10,000 threshold.
  - `etsy_offsite_ads_12`: 12% Offsite Ads tier for high-volume qualifying merchants.
  - `shopify_payments`: 2.9% + $0.30 payment processing fee (zero marketplace listing or transaction tax).
  - `tiktok_shop_us`: 6.0% transaction fee (2026 standard) + $0.30 fixed fee per order.
- **Break-Even & Target Margin Solver**: Inversely solves the exact retail price required to achieve any targeted net margin percentage (e.g. 35%, 50%) after factoring in base blank cost, factory shipping, and channel take rates.
- **Coupon Discount Stress Tester**: Simulates standard marketing discounts (10%, 15%, 20%, 25%, 30%) to ensure automated promotions never push net profit into negative territory.
- **Zero-Egress Financial Privacy**: All unit economic models run on loopback (`127.0.0.1:8120`) without exposing merchant revenue, unit margins, or supplier costs.

---

## 🚀 Quick Start

```bash
# Clone and launch the standalone daemon on port 8120
git clone https://github.com/1nc0gn30/pod-margin-sentinel.git
cd pod-margin-sentinel
python3 server.py --port 8120

# Query daemon health and product benchmarks:
curl -s http://127.0.0.1:8120/health
curl -s http://127.0.0.1:8120/api/benchmarks
```

---

## 💻 ZothOS CLI & MCP Commands

The sovereign binary `pod-margin-sentinel` is pre-installed in `/usr/local/bin` and `~/.local/bin`:

```bash
# Verify installation & status
pod-margin-sentinel --version
pod-margin-sentinel --status
pod-margin-sentinel --json

# Calculate order profit on Etsy
pod-margin-sentinel calc --retail 34.99 --wholesale 12.50 --shipping 5.49 --platform etsy_organic

# Compare profit across all channels side-by-side
pod-margin-sentinel compare --retail 34.99 --wholesale 12.50 --shipping 5.49
pod-margin-sentinel compare --retail 34.99 --wholesale 12.50 --shipping 5.49 --json

# Solve for break-even and 35% target margin retail price
pod-margin-sentinel breakeven --wholesale 12.50 --shipping 5.49 --target-margin 35.0

# Stress-test promotional coupon discounts
pod-margin-sentinel coupon --retail 34.99

# Launch server daemon
pod-margin-sentinel server --port 8120
```

---

## ☕ 100% Free & Open-Access Support Architecture

Every tool engineered by Neal Frazier Tech is **100% free, open, and unlocked by default**. There are zero paywalls, zero license locks, and zero feature gates.

If this tool protects your profit margins or automates your pricing strategy, consider supporting development:

- **☕ Buy Us a Coffee (Stripe)**: [https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X](https://buy.stripe.com/3cIfZg27PdKo2D64Ocfw40X)
- **◎ Solana Tip Address**: `GG2eQbVh8ut1BK6j1A2tz7pSySdLpD38BgyEhGcxdXoK`

---

<div align="center">
  <sub>Engineered by <b>Neal Frazier Tech</b> (<a href="https://github.com/1nc0gn30">@1nc0gn30</a>) &bull; <a href="https://nullai.tech">NullAI Platform</a> &bull; <a href="https://zoth.nullai.tech">Zoth Studio v2</a></sub>
</div>
