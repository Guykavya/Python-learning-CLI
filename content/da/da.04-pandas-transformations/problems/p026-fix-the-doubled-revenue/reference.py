import pandas as pd


def revenue_report(orders, payments):
    """Revenue report: one row per order with its payment status."""
    # 1. bring payments to the grain of the orders table: one row per order
    pay = (payments.assign(is_paid=payments["status"] == "paid")
                   .groupby("order_id", as_index=False)
                   .agg(n_payments=("payment_id", "size"), paid=("is_paid", "any")))
    # 2. now the merge is one-to-one, and pandas checks it
    table = orders.merge(pay, on="order_id", how="left", validate="1:1")
    assert len(table) == len(orders), "the merge changed the number of orders"
    # 3. orders without any attempt
    table["n_payments"] = table["n_payments"].fillna(0).astype(int)
    table["paid"] = table["paid"].fillna(False).astype(bool)
    return {
        "total_revenue": float(table["amount"].sum()),
        "orders": len(table),
        "paid_orders": int(table["paid"].sum()),
        "table": table[["order_id", "customer_id", "amount", "n_payments", "paid"]],
    }
