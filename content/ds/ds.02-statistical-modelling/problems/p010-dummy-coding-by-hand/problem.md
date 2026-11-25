# Dummy coding by hand

Chapter section 6.3. A category with `k` levels becomes `k - 1` columns of 0/1 (dummies). The level left out is the **baseline**: its rows have 0 in every dummy column.

```python
def dummies(series, baseline):
    levels = sorted(set(series) - {baseline})
    return {f"is_{lv}": [int(v == lv) for v in series] for lv in levels}


education = ["school", "masters", "degree", "degree", "school"]
d = dummies(education, "school")
for name, column in d.items():
    print(name, column)
n_baseline = sum(1 for i in range(len(education)) if all(d[name][i] == 0 for name in d))
print("rows in the baseline group:", n_baseline)
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `education = ["school", "degree"]` the dictionary would have one column, and the program would print `is_degree [0, 1]` and then `rows in the baseline group: 1`.

## After you answer

- Why can we not keep a dummy for the baseline as well? (Think about the sum of the columns and the constant.)
