"""POD Margin Sentinel - Exact 2026 Multi-Platform Fee Architecture.

Defines exact mathematical fee schedules for Etsy, Shopify, TikTok Shop,
and baseline Printify/Gelato wholesale manufacturing baselines.
100% Python Standard Library.
"""

from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass(frozen=True)
class PlatformFeeSpec:
    platform_name: str
    transaction_percent: float
    payment_processing_percent: float
    payment_processing_fixed: float
    listing_fixed: float
    offsite_ads_percent: float
    notes: str
    offsite_ads_cap: float = 0.0  # max Offsite Ads fee per order in USD (0 = no cap)

PLATFORM_FEES: Dict[str, PlatformFeeSpec] = {
    "etsy_organic": PlatformFeeSpec(
        platform_name="Etsy (Organic Search / Direct)",
        transaction_percent=0.065,            # 6.5% on total order (item + shipping)
        payment_processing_percent=0.030,     # 3.0% Etsy Payments
        payment_processing_fixed=0.25,        # $0.25 fixed
        listing_fixed=0.20,                   # $0.20 auto-renew
        offsite_ads_percent=0.0,
        notes="Standard organic Etsy sale without external advertising attribution."
    ),
    "etsy_offsite_ads_15": PlatformFeeSpec(
        platform_name="Etsy (Offsite Ads 15% Tier)",
        transaction_percent=0.065,
        payment_processing_percent=0.030,
        payment_processing_fixed=0.25,
        listing_fixed=0.20,
        offsite_ads_percent=0.15,             # 15% mandatory for sellers < $10k/yr
        notes="Customer discovered via Google/Facebook/Pinterest ads placed by Etsy.",
        offsite_ads_cap=100.0,                # Etsy caps the Offsite Ads fee at $100/order
    ),
    "etsy_offsite_ads_12": PlatformFeeSpec(
        platform_name="Etsy (Offsite Ads 12% Tier)",
        transaction_percent=0.065,
        payment_processing_percent=0.030,
        payment_processing_fixed=0.25,
        listing_fixed=0.20,
        offsite_ads_percent=0.12,             # 12% discounted tier for sellers > $10k/yr
        notes="High-volume seller discounted Offsite Ads attribution tier.",
        offsite_ads_cap=100.0
    ),
    "shopify_payments": PlatformFeeSpec(
        platform_name="Shopify (Shopify Payments Basic)",
        transaction_percent=0.0,              # 0% transaction fee with Shopify Payments
        payment_processing_percent=0.029,     # 2.9% credit card processing
        payment_processing_fixed=0.30,        # $0.30 fixed
        listing_fixed=0.0,                    # Zero listing fee
        offsite_ads_percent=0.0,
        notes="Direct-to-consumer store hosted on Shopify with no marketplace commissions."
    ),
    "tiktok_shop": PlatformFeeSpec(
        platform_name="TikTok Shop (US 2026)",
        transaction_percent=0.060,            # 6.0% referral fee
        payment_processing_percent=0.0,       # Included in referral fee
        payment_processing_fixed=0.30,        # $0.30 fixed transaction fee
        listing_fixed=0.0,
        offsite_ads_percent=0.0,
        notes="US TikTok Shop commerce affiliate marketplace order."
    )
}

# Standard POD product benchmarks (typical base wholesale + domestic shipping)
CATALOG_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "gildan_18000": {
        "title": "Gildan 18000 Crewneck Sweatshirt",
        "category": "Apparel",
        "recommended_retail": 34.99,
        "printify_base_cost": 12.50,
        "printify_shipping": 5.49,
        "gelato_base_cost": 14.20,
        "gelato_shipping": 5.20,
    },
    "comfort_colors_1717": {
        "title": "Comfort Colors 1717 Garment-Dyed Tee",
        "category": "Apparel",
        "recommended_retail": 29.99,
        "printify_base_cost": 10.80,
        "printify_shipping": 4.79,
        "gelato_base_cost": 11.90,
        "gelato_shipping": 4.50,
    },
    "bella_canvas_3001": {
        "title": "Bella+Canvas 3001 Unisex Jersey Tee",
        "category": "Apparel",
        "recommended_retail": 26.99,
        "printify_base_cost": 8.90,
        "printify_shipping": 4.79,
        "gelato_base_cost": 9.40,
        "gelato_shipping": 4.50,
    },
    "ceramic_mug_15oz": {
        "title": "White Gloss Ceramic Mug 15oz",
        "category": "Drinkware",
        "recommended_retail": 21.99,
        "printify_base_cost": 6.80,
        "printify_shipping": 6.99,
        "gelato_base_cost": 7.40,
        "gelato_shipping": 6.50,
    },
    "canvas_gallery_wrap_16x20": {
        "title": "Stretched Canvas Gallery Wrap 16x20",
        "category": "Wall Art",
        "recommended_retail": 49.99,
        "printify_base_cost": 18.50,
        "printify_shipping": 9.99,
        "gelato_base_cost": 19.80,
        "gelato_shipping": 9.50,
    },
    "canvas_tote_heavyweight": {
        "title": "Heavyweight Cotton Market Tote",
        "category": "Accessories",
        "recommended_retail": 24.99,
        "printify_base_cost": 7.20,
        "printify_shipping": 4.99,
        "gelato_base_cost": 7.90,
        "gelato_shipping": 4.80,
    },
    "digital_wall_art_pack": {
        "title": "5-Ratio Digital Art Download Pack",
        "category": "Digital Download",
        "recommended_retail": 9.99,
        "printify_base_cost": 0.00,
        "printify_shipping": 0.00,
        "gelato_base_cost": 0.00,
        "gelato_shipping": 0.00,
    }
}

def get_benchmarks_list() -> List[Dict[str, Any]]:
    res = []
    for k, v in CATALOG_BENCHMARKS.items():
        res.append({"sku": k, **v})
    return res
