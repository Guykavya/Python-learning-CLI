# Weighted or unweighted

Chapter section 6.1 and 6.3. Seven jobs in three cities. Combine the city averages in two ways and compare each with the direct average over all jobs.

```python
import numpy as np
import pandas as pd

jobs = pd.DataFrame({
    "city": ["Pune", "Pune", "Pune", "Pune", "Delhi", "Jaipur", "Jaipur"],
    "quote_total": [100, 200, 300, 400, 600, 100, 200],
})

g = jobs.groupby("city")["quote_total"].agg(["count", "mean"])
print(g["count"].tolist(), g["mean"].tolist())
print(round(float(g["mean"].mean()), 2))
print(round(float(np.average(g["mean"], weights=g["count"])), 2))
print(round(float(jobs["quote_total"].mean()), 2))
print(round(float(g["mean"].mean() - jobs["quote_total"].mean()), 2))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For two groups with means `10` (3 jobs) and `20` (1 job), the simple mean of the means is `15.0`, but the weighted mean is `(10*3 + 20*1) / 4 = 12.5`, which is the mean of the four jobs.

## After you answer

- Why is the simple mean of the three city means wrong, even though every city mean is right?
- The weighted mean equals the direct mean over all jobs. Why is that always true, and what must the weights be?
- Which city pulls the simple mean up, and by how much does it miss?
