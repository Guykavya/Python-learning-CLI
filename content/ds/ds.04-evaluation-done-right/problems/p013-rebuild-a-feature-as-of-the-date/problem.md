# Rebuild a feature as of the date

Chapter sections 4.5 and 7. Many leaks hide in "total so far" columns that were computed on the **final** data. The fix is to rebuild the feature **as of the prediction date**: count only what had happened **before** that moment.

Write `as_of_feature(events, customers)`:

- `events`: a DataFrame with columns `customer_id` and `day` (one row per support call, say)
- `customers`: a DataFrame with columns `customer_id` and `predict_day` (one row per customer)
- return a `pandas.Series` named `"events_before"`, indexed by `customer_id` in the order of `customers`, with the number of events of that customer whose `day` is **strictly before** its `predict_day` (an event on the prediction day itself is not counted). Customers without events get 0. The values are integers.

## Example

```text
events:    (1, 3), (1, 9), (1, 10), (1, 15), (2, 1)
customers: (1, predict_day 10), (2, 5), (3, 7)
-> customer 1: 2  (days 3 and 9; day 10 is not before day 10)   customer 2: 1   customer 3: 0
```
