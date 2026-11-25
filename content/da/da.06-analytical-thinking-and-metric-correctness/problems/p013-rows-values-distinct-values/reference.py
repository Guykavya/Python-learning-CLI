def three_counts(payments):
    return {
        "rows": int(len(payments)),
        "with_method": int(payments["method"].count()),
        "distinct_customers": int(payments["customer_id"].nunique()),
    }
