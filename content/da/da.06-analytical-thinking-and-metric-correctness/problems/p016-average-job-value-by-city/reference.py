def avg_job_value(jobs, customers):
    joined = jobs.merge(customers[["customer_id", "city"]], on="customer_id", how="left", validate="m:1")
    by_city = joined.groupby("city")["quote_total"].mean()
    return {
        "overall": float(jobs["quote_total"].sum() / len(jobs)),
        "by_city": {city: float(v) for city, v in by_city.items()},
    }
