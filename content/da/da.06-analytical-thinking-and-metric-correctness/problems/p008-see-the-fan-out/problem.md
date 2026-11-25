# See the fan-out

Chapter section 4.1 and 4.2. Four jobs are joined to their seven line items. Count what the join does to rows, sums and averages, and what still gives the right answer.

```python
import pandas as pd

jobs = pd.DataFrame({"job_id": [1, 2, 3, 4], "quote_total": [1000, 400, 700, 300]})
items = pd.DataFrame({"job_id": [1, 1, 1, 2, 3, 3, 4], "line_no": [1, 2, 3, 1, 1, 2, 1]})

j = jobs.merge(items, on="job_id")
print(len(j), j["job_id"].nunique())
print(int(j["quote_total"].sum()), int(jobs["quote_total"].sum()))
print(round(float(j["quote_total"].mean()), 2), round(float(jobs["quote_total"].mean()), 2))
print(j.groupby("job_id").size().tolist())
print(int(j.drop_duplicates("job_id")["quote_total"].sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `a = pd.DataFrame({"k": [1, 2], "v": [10, 20]})` and `b = pd.DataFrame({"k": [1, 1, 2]})`, `a.merge(b, on="k")` has 3 rows and `v.sum()` of the result is `40` (10 + 10 + 20), while `a["v"].sum()` is `30`.

## After you answer

- Which of the printed numbers is the number of jobs, and which is only the number of lines?
- Why is the average quote after the join higher than the true average? Which job pulls it up, and by how much?
- Write the one-line rule that makes the last number right.
