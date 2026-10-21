# Interleave two words

Read two lines (each may be empty). Build a new string by taking one character from the first
line, then one from the second, then one from the first again, and so on. When one line runs
out, add the **rest** of the other line at the end.

**Examples**

| First | Second | Output |
|---|---|---|
| `abc` | `123` | `a1b2c3` |
| `abc` | `12345` | `a1b2c345` |
| `hello` | `XY` | `hXeYllo` |

If both lines are empty, print `(empty)`.
