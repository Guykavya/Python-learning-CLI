## Hint 1

Where does the city of a job live: in `jobs` or in `customers`? How do you bring it over without changing the number of
jobs? Which two numbers must you add up to get the overall mean, and which easy mistake gives you a different overall number?

## Hint 2

```text
joined = jobs merged with customers[["customer_id", "city"]] on customer_id, validate="m:1"
by_city = joined grouped by city, mean of quote_total
overall = sum of jobs.quote_total / number of jobs         (not the mean of by_city)
return {"overall": float, "by_city": {city: float}}
```
