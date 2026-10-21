## Walkthrough

| t | chain prints | `t > 20` | `t >= 40` |
|---|---|---|---|
| 5 | `5 cold` | no | no |
| 18 | `18 mild` | no | no |
| 25 | `25 warm` | `fan on` | no |
| 31 | `31 hot` | `fan on` | no |
| 40 | `40 hot` | `fan on` | `alert` |

The chain picks one line per value: the first true condition wins. The two plain `if`s are
separate decisions, so 40 gets three lines.

The last part: `code == "a"` is `False`, so `or` returns `"c"`, which is truthy. The `if`
runs and prints `matched b`. The correct test is `code == "a" or code == "c"`.
