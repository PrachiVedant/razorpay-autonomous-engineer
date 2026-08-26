from merchant.analytics import (
    get_revenue_metrics,
    get_payment_metrics,
    get_payment_method_metrics,
)


def get_merchant_snapshot():
    """
    Return a complete deterministic snapshot of merchant performance.
    """

    revenue = get_revenue_metrics()
    payments = get_payment_metrics()
    payment_methods = get_payment_method_metrics()

    return {
        "revenue": revenue,
        "payments": payments,
        "payment_methods": payment_methods,
    }