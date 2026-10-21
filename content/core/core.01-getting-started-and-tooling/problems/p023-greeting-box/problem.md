# A box that fits any name

Read a name with `input()` (no prompt). Build the message `Hello, <name>!` and
print it inside a box that is exactly as wide as needed, with exactly **one
space** on each side of the message. For `Asha`:

```
+--------------+
|              |
| Hello, Asha! |
|              |
+--------------+
```

Rules:

- The message is `Hello, ` + name + `!`.
- Top and bottom: `+`, then (length of message + 2) dashes, then `+`.
- The empty lines: `|`, then (length of message + 2) spaces, then `|`.
- The middle line: `| `, the message, ` |`.

It must work for any name, including names with spaces. You may not use `if`
or loops; `len()` and `*` are enough.

**Example**

Input:
```
Ravi Kumar
```
Output:
```
+--------------------+
|                    |
| Hello, Ravi Kumar! |
|                    |
+--------------------+
```
