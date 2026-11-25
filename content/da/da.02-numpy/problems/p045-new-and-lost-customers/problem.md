# New and lost customers

Chapter section 15.5 (set operations). You have the customer ids that bought something in January and in February (1-D arrays; a customer who bought several times appears several times). Write `customer_changes(jan_ids, feb_ids)` that returns a tuple of three arrays `(new, lost, kept)`:

- `new`: ids that bought in February but not in January;
- `lost`: ids that bought in January but not in February;
- `kept`: ids that bought in both months.

Each array is **sorted** and has **no duplicates**, and keeps the dtype of the ids (integers stay integers, string ids stay strings). An empty month is allowed. No Python loops or Python `set`s.

## Example

```python
jan = np.array([101, 102, 102, 103, 105])
feb = np.array([102, 104, 105, 105, 106])
new, lost, kept = customer_changes(jan, feb)
new.tolist(), lost.tolist(), kept.tolist()
# ([104, 106], [101, 103], [102, 105])
```
