# The grain of a result

Chapter sections 2.4 and 2.5. Every result has a grain, including the ones you never save. Jobs are joined to their line items, grouped by city, and deduplicated. After each step, ask: what is one row now, and is a candidate key still unique?

```python
import pandas as pd

jobs = pd.DataFrame({"job_id": [1, 2, 3], "city": ["Pune", "Delhi", "Pune"], "quote_total": [500, 300, 900]})
items = pd.DataFrame({"job_id": [1, 1, 2, 3, 3, 3], "line_no": [1, 2, 1, 1, 2, 9],
                      "item": ["labour", "parts", "labour", "labour", "parts", "travel"]})

j = jobs.merge(items, on="job_id")
print(len(j))
print(j.duplicated(subset=["job_id"]).any(), j.duplicated(subset=["job_id", "line_no"]).any(),
      j.duplicated(subset=["city", "item"]).any())

by_city = j.groupby("city", as_index=False).agg(lines=("line_no", "size"), quote=("quote_total", "sum"))
print(by_city["lines"].tolist(), by_city["quote"].tolist())
print(by_city.duplicated(subset=["city"]).any())

one = j.drop_duplicates(subset=["job_id"])
print(len(one), one.duplicated(subset=["job_id"]).any(), int(one["quote_total"].sum()))
print(int(j["quote_total"].sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `d = pd.DataFrame({"k": [1, 1, 2]})`, `print(d.duplicated(subset=["k"]).any())` prints `True` (key 1 repeats), and after `d = d.drop_duplicates(subset=["k"])` the same line prints `False`.

## After you answer

- After the merge, what is one row? Which of the three candidate keys is still a key, and why?
- `quote_total` is a job-level number. Why is the last sum (4000) not the sum of the job quotes (1700)?
- What would `by_city["quote"]` have said about Pune if the grain had been checked before the `groupby`?
