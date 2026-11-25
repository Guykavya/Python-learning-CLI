# Filters as a pure function

Chapter section 9.2. The dashboard's filters live in a plain function that a test can call, outside Streamlit. An **empty** list means "the reader selected nothing", which is **not** the same as
"everything": the function returns `None` and the app shows a message. A selection that matches customers who have **no panel rows** also returns `None`.

```python
import pandas as pd


def filter_data(customers, panel, channels, plans, cities):
    if not channels or not plans or not cities:
        return None
    cus = customers[customers["channel"].isin(channels) & customers["plan"].isin(plans) & customers["city"].isin(cities)]
    pan = panel[panel["customer_id"].isin(cus["customer_id"])]
    return (cus, pan) if len(pan) else None


customers = pd.DataFrame({
    "customer_id": range(1, 9),
    "channel": ["paid", "paid", "organic", "organic", "referral", "paid", "organic", "referral"],
    "plan": ["2-meal", "3-meal", "2-meal", "3-meal", "2-meal", "2-meal", "3-meal", "3-meal"],
    "city": ["Metro", "Small", "Metro", "Large", "Small", "Large", "Metro", "Metro"],
})
panel = pd.DataFrame({"customer_id": [1, 1, 2, 3, 3, 3, 4, 6, 6, 7, 8], "week": range(11)})

combos = [
    (["paid"], ["2-meal", "3-meal"], ["Metro", "Small", "Large"]),
    (["referral"], ["2-meal"], ["Small"]),
    (["organic", "referral"], ["3-meal"], ["Metro"]),
    ([], ["2-meal"], ["Metro"]),
]
for ch, pl, ci in combos:
    out = filter_data(customers, panel, ch, pl, ci)
    print("None" if out is None else f"{len(out[0])} {len(out[1])}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `(["organic"], ["2-meal"], ["Metro"])` the line would be `1 3` (customer 3, with three panel rows).

## After you answer

- Which customer has no panel rows, and which combination does that affect?
- Why should an empty list not mean "all"?
