# State, transition, base case

A frog climbs a staircase and each jump is **1, 3 or 4** steps. `f[i]` is the number of jump sequences that land exactly on step `i` (order matters: `1 + 3` and `3 + 1` are different). The recipe of chapter section 2:

- **State:** `f[i]` = the number of ways to land on step `i`.
- **Transition:** `f[i] = f[i - 1] + f[i - 3] + f[i - 4]`, using only the terms whose index is `>= 0`.
- **Base case:** `f[0] = 1`.

This program fills the table and prints how each cell is made. Predict **exactly** what it prints. Do not run it.

```python
steps = [1, 3, 4]
n = 8

f = [0] * (n + 1)
f[0] = 1
print("f[0] = 1  (base case)")
for i in range(1, n + 1):
    used = []
    for s in steps:
        if i - s >= 0:
            f[i] += f[i - s]
            used.append("f[" + str(i - s) + "]")
    terms = " + ".join(used)
    print(f"f[{i}] = {terms} = {f[i]}")
print("table:", f)
print("answer:", f[n])
```

Write your answer in `answer.txt`, one printed line per line (11 lines).

## Example of the format

The first two lines are:

```text
f[0] = 1  (base case)
f[1] = f[0] = 1
```

For `i = 1` only the step 1 fits (`1 - 3` and `1 - 4` are negative), so the list `used` has one entry and `" + ".join` adds no plus sign.

## How to work

1. Draw nine boxes `f[0]` to `f[8]` on paper. Fill `f[0] = 1`.
2. For each `i`, write which of `i - 1`, `i - 3`, `i - 4` are `>= 0`, **in that order** (the order of `steps`), then add the boxes.
3. Check one cell by listing the sequences: `f[4]` should count `1111`, `13`, `31` and `4`.

## After you answer

1. Why is `f[0] = 1` and not 0? What would every cell be if it were 0?
2. List the ways to land on step 5 and check that there are as many as `f[5]`.
3. Which line of the code is the base-case logic "steps below 0 do not exist" in disguise?
