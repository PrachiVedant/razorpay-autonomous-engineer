from merchant.data import (
    get_orders,
    get_payments,
)


def get_revenue_metrics():

    orders = get_orders()

    paid_orders = [
        order
        for order in orders
        if order["status"] == "paid"
    ]

    abandoned_orders = [
        order
        for order in orders
        if order["status"] == "abandoned"
    ]

    revenue = sum(
        order["amount"]
        for order in paid_orders
    )

    abandoned_revenue = sum(
        order["amount"]
        for order in abandoned_orders
    )

    total_orders = len(orders)

    paid_count = len(paid_orders)

    conversion_rate = (
        paid_count / total_orders * 100
        if total_orders
        else 0
    )

    return {
        "total_orders": total_orders,
        "paid_orders": paid_count,
        "abandoned_orders": len(abandoned_orders),
        "revenue": revenue,
        "abandoned_revenue": abandoned_revenue,
        "conversion_rate": round(
            conversion_rate,
            2,
        ),
    }


def get_payment_metrics():

    payments = get_payments()

    total = len(payments)

    successful = [
        payment
        for payment in payments
        if payment["status"] == "success"
    ]

    failed = [
        payment
        for payment in payments
        if payment["status"] == "failed"
    ]

    success_rate = (
        len(successful) / total * 100
        if total
        else 0
    )

    failed_value = sum(
        payment["amount"]
        for payment in failed
    )

    return {
        "total_payments": total,
        "successful_payments": len(successful),
        "failed_payments": len(failed),
        "success_rate": round(
            success_rate,
            2,
        ),
        "failed_payment_value": failed_value,
    }


def get_payment_method_metrics():

    payments = get_payments()

    metrics = {}

    for payment in payments:

        method = payment["method"]

        if method not in metrics:

            metrics[method] = {
                "total": 0,
                "failed": 0,
                "amount": 0,
            }

        metrics[method]["total"] += 1

        metrics[method]["amount"] += (
            payment["amount"]
        )

        if payment["status"] == "failed":

            metrics[method]["failed"] += 1

    for method, data in metrics.items():

        data["failure_rate"] = round(
            data["failed"]
            / data["total"]
            * 100,
            2,
        )

    return metrics