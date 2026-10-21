## Walkthrough

| Code | Output | Why |
|---|---|---|
| loop over `scores.items()` | `asha 6`, `ravi 10` | each pair is unpacked into `name, s` |
| `pairs[1]` | `('b', 2)` | `zip` makes tuples |
| `enumerate(pairs)` | `0 a`, `1 bb`, `2 ccc` | `(letter, n)` unpacks the inner tuple; `letter * n` repeats the letter |
| star in the loop | `x [1, 2, 3] 6`, `y [4] 4` | `*nums` collects the rest as a list |
| after `first = first * 10` | `[[1, 2], [3, 4]]` | the name `first` was rebound to a new int; the list was not touched |
| after `row[0] = row[0] * 10` | `[[10, 2], [30, 4]]` | `row` refers to the real inner list, so assigning to `row[0]` changes it |
