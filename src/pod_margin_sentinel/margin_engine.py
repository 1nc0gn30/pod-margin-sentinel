"""POD Margin Sentinel - Mathematical Margin Engine & Break-Even Simulator.

Precision algorithmic calculation of marketplace commissions, gateway fees,
net margin velocity, break-even thresholds, and discount elasticity.
100% Python Standard Library.
"""

from typing import Dict, Any, List
from .fee_structures import PLATFORM_FEES, PlatformFeeSpec, CATALOG_BENCHMARKS

class MarginEngine:
    """Core financial logic for Print-on-Demand commerce operations."""

    @staticmethod
    def calculate_order_profit(
        retail_price: float,
        wholesale_cost: float,
        factory_shipping: float,
        shipping_charged: float = 0.0,
        platform_key: str = "etsy_organic",
        discount_percent: float = 0.0,
        ad_spend_per_order: float = 0.0
    ) -> Dict[str, Any]:
        """Calculates granular profit and loss metrics for a single POD transaction."""
        fee_spec = PLATFORM_FEES.get(platform_key, PLATFORM_FEES["etsy_organic"])

        discount_mult = max(0.0, 1.0 - (discount_percent / 100.0))
        discounted_item_price = round(retail_price * discount_mult, 2)
        gross_revenue = round(discounted_item_price + shipping_charged, 2)

        # 1. Platform & Processing Fees
        tx_fee = round(gross_revenue * fee_spec.transaction_percent, 2)
        pp_fee = round((gross_revenue * fee_spec.payment_processing_percent) + fee_spec.payment_processing_fixed, 2)
        listing_fee = fee_spec.listing_fixed
        offsite_fee = round(gross_revenue * fee_spec.offsite_ads_percent, 2)
        ad_spend = round(ad_spend_per_order, 2)

        total_fees = round(tx_fee + pp_fee + listing_fee + offsite_fee + ad_spend, 2)

        # 2. Manufacturing & Fulfillment Costs (COGS)
        total_cogs = round(wholesale_cost + factory_shipping, 2)

        # 3. Net Financials
        net_profit = round(gross_revenue - total_fees - total_cogs, 2)
        net_margin_pct = round((net_profit / gross_revenue * 100.0) if gross_revenue > 0 else 0.0, 2)
        markup_mult = round((gross_revenue / total_cogs) if total_cogs > 0 else 999.0, 2)

        # Health tier assignment
        if net_margin_pct >= 40.0:
            health = "SOVEREIGN_GOLDEN"
            health_label = "Optimal Golden Margin (>40%)"
        elif net_margin_pct >= 25.0:
            health = "HEALTHY"
            health_label = "Healthy Commercial Margin (25-40%)"
        elif net_margin_pct >= 10.0:
            health = "MODERATE"
            health_label = "Slim Operating Margin (10-25%)"
        elif net_margin_pct > 0.0:
            health = "CRITICAL_LOW"
            health_label = "Vulnerable Thin Margin (<10%)"
        else:
            health = "NET_LOSS"
            health_label = "Underwater / Negative Margin (LOSS)"

        return {
            "platform": fee_spec.platform_name,
            "platform_key": platform_key,
            "pricing": {
                "retail_price": retail_price,
                "discount_percent": discount_percent,
                "discounted_item_price": discounted_item_price,
                "shipping_charged": shipping_charged,
                "gross_revenue": gross_revenue
            },
            "cogs": {
                "wholesale_base": wholesale_cost,
                "factory_shipping": factory_shipping,
                "total_cogs": total_cogs
            },
            "fees_breakdown": {
                "transaction_fee": tx_fee,
                "payment_processing": pp_fee,
                "listing_auto_renew": listing_fee,
                "offsite_ads_fee": offsite_fee,
                "ad_spend_direct": ad_spend,
                "total_fees": total_fees
            },
            "profitability": {
                "net_dollar_profit": net_profit,
                "net_margin_percent": net_margin_pct,
                "markup_multiplier": markup_mult,
                "health_tier": health,
                "health_label": health_label,
                "is_profitable": net_profit > 0
            }
        }

    @classmethod
    def calculate_break_even_price(
        cls,
        wholesale_cost: float,
        factory_shipping: float,
        shipping_charged: float = 0.0,
        platform_key: str = "etsy_organic"
    ) -> float:
        """Solves for exact retail price needed to achieve exactly $0.00 net profit."""
        fee_spec = PLATFORM_FEES.get(platform_key, PLATFORM_FEES["etsy_organic"])
        total_cogs = wholesale_cost + factory_shipping
        fixed_fees = fee_spec.payment_processing_fixed + fee_spec.listing_fixed
        variable_rate = fee_spec.transaction_percent + fee_spec.payment_processing_percent + fee_spec.offsite_ads_percent

        # Net Profit = (Retail + ShipCharged) * (1 - variable_rate) - fixed_fees - total_cogs = 0
        # (Retail + ShipCharged) * (1 - variable_rate) = total_cogs + fixed_fees
        # Retail = (total_cogs + fixed_fees) / (1 - variable_rate) - ShipCharged
        denominator = 1.0 - variable_rate
        if denominator <= 0:
            return round(total_cogs * 2.0, 2)

        break_even = (total_cogs + fixed_fees) / denominator - shipping_charged
        return max(0.0, round(break_even, 2))

    @classmethod
    def recommend_retail_price(
        cls,
        wholesale_cost: float,
        factory_shipping: float,
        target_margin_percent: float = 35.0,
        shipping_charged: float = 0.0,
        platform_key: str = "etsy_organic"
    ) -> float:
        """Calculates target retail price required to achieve specified net margin percentage."""
        fee_spec = PLATFORM_FEES.get(platform_key, PLATFORM_FEES["etsy_organic"])
        total_cogs = wholesale_cost + factory_shipping
        fixed_fees = fee_spec.payment_processing_fixed + fee_spec.listing_fixed
        variable_rate = fee_spec.transaction_percent + fee_spec.payment_processing_percent + fee_spec.offsite_ads_percent
        target_rate = target_margin_percent / 100.0

        # Net Profit = Revenue * target_rate
        # Revenue * (1 - variable_rate) - fixed_fees - total_cogs = Revenue * target_rate
        # Revenue * (1 - variable_rate - target_rate) = total_cogs + fixed_fees
        # Revenue = (total_cogs + fixed_fees) / (1 - variable_rate - target_rate)
        denominator = 1.0 - variable_rate - target_rate
        if denominator <= 0:
            return round(total_cogs * 3.0, 2)

        recommended_gross = (total_cogs + fixed_fees) / denominator
        recommended_price = recommended_gross - shipping_charged
        return max(0.0, round(recommended_price, 2))

    @classmethod
    def compare_all_platforms(
        cls,
        retail_price: float,
        wholesale_cost: float,
        factory_shipping: float,
        shipping_charged: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Generates side-by-side comparison across all major platforms."""
        results = []
        for key in PLATFORM_FEES.keys():
            calc = cls.calculate_order_profit(
                retail_price=retail_price,
                wholesale_cost=wholesale_cost,
                factory_shipping=factory_shipping,
                shipping_charged=shipping_charged,
                platform_key=key
            )
            results.append({
                "platform_key": key,
                "platform_name": calc["platform"],
                "gross_revenue": calc["pricing"]["gross_revenue"],
                "total_fees": calc["fees_breakdown"]["total_fees"],
                "net_profit": calc["profitability"]["net_dollar_profit"],
                "net_margin_percent": calc["profitability"]["net_margin_percent"],
                "health_tier": calc["profitability"]["health_tier"]
            })
        return results

    @classmethod
    def evaluate_coupon_safety(
        cls,
        retail_price: float,
        wholesale_cost: float,
        factory_shipping: float,
        shipping_charged: float = 0.0,
        platform_key: str = "etsy_organic",
        min_acceptable_margin: float = 15.0
    ) -> Dict[str, Any]:
        """Audits standard discount tiers (10%, 15%, 20%, 25%, 30%) for margin safety."""
        tiers = [10.0, 15.0, 20.0, 25.0, 30.0]
        evaluations = []
        max_safe_coupon = 0.0

        for disc in tiers:
            res = cls.calculate_order_profit(
                retail_price=retail_price,
                wholesale_cost=wholesale_cost,
                factory_shipping=factory_shipping,
                shipping_charged=shipping_charged,
                platform_key=platform_key,
                discount_percent=disc
            )
            margin = res["profitability"]["net_margin_percent"]
            is_safe = margin >= min_acceptable_margin
            if is_safe:
                max_safe_coupon = disc

            evaluations.append({
                "discount_percent": disc,
                "discounted_price": res["pricing"]["discounted_item_price"],
                "net_profit": res["profitability"]["net_dollar_profit"],
                "net_margin_percent": margin,
                "is_safe": is_safe,
                "status": "APPROVED" if is_safe else ("RISK" if margin > 0 else "UNACCEPTABLE")
            })

        return {
            "retail_price": retail_price,
            "min_acceptable_margin": min_acceptable_margin,
            "max_safe_coupon_percent": max_safe_coupon,
            "discount_scenarios": evaluations
        }
