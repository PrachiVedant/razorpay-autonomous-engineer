from merchant.analytics import (
    get_revenue_metrics,
    get_payment_metrics,
    get_payment_method_metrics,
)

from merchant.data import (
    get_products,
)

#snapshot

def get_merchant_snapshot():
    """
    Return the complete merchant snapshot used by the
    autonomous growth workflow.

    The Growth Agent receives merchant information through
    this interface instead of directly reading JSON files.
    """

    revenue = get_revenue_metrics()
    payments = get_payment_metrics()
    payment_methods = get_payment_method_metrics()
    products = get_products()

    return {
        "revenue": revenue,
        "payments": payments,
        "payment_methods": payment_methods,
        "products": products,
        "upsell_evidence": _get_upsell_evidence(),
    }
#evidence

def _get_upsell_evidence():
    """
    Return deterministic historical evidence for the
    bounded upsell opportunity.

    This evidence is used only to identify an opportunity.

    It does NOT authorize a transaction.

    Financial authorization remains the responsibility
    of the deterministic policy layer.
    """

    return [
        {
            "base_product": "Premium Annual Plan",
            "upsell_product": "Premium Support",
            "upsell_price": 5000,
            "conversion_rate": 0.25,
        }
    ]


def get_growth_evidence():
    """
    Return only the merchant information required for
    growth opportunity identification.
    """

    snapshot = get_merchant_snapshot()

    return {
        "revenue": snapshot["revenue"],
        "payments": snapshot["payments"],
        "payment_methods": snapshot["payment_methods"],
        "products": snapshot["products"],
        "upsell_evidence": snapshot["upsell_evidence"],
    }

