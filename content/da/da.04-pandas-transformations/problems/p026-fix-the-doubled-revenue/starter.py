import pandas as pd


def revenue_report(orders, payments):
    """Revenue report: one row per order with its payment status."""
    table = orders.merge(payments, on="order_id", how="left")
    table["paid"] = table["status"] == "paid"
    table["n_payments"] = table.groupby("order_id")["payment_id"].transform("count")
    return {
        "total_revenue": float(table["amount"].sum()),
        "orders": len(table),
        "paid_orders": int(table["paid"].sum()),
        "table": table[["order_id", "customer_id", "amount", "n_payments", "paid"]],
    }
