# Parse unified-diff hunk headers

`git diff` prints changes as **hunks**. Each hunk starts with a header line like

```text
@@ -12,3 +12,4 @@ def greet(name):
```

It means: in the old file the hunk starts at line 12 and covers 3 lines; in the new file it
starts at line 12 and covers 4 lines. Text after the second `@@` is an optional section heading.
When a length is `1`, git leaves it out: `@@ -5 +5,2 @@` means old length 1.

Write `parse_hunks(text: str) -> list[tuple[int, int, int, int]]` that returns
`(old_start, old_len, new_start, new_len)` for every hunk header in a whole diff, in order.

- A header is a line that **starts** with `@@ -` and has the shape
  `@@ -A[,B] +C[,D] @@` (anything may follow). `A`, `B`, `C`, `D` are non-negative integers.
- A missing length means 1.
- All four values are `int`s.
- Lines that only *contain* a header-like text somewhere else (for example a removed line
  `-@@ -1 +1 @@` or a context line with a leading space) are **not** headers.
- Lines that look like a header but are malformed (letters instead of numbers, a missing `+`
  part) are skipped.

**Example**

```python
diff = """diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 import sys
+import os
 print("hi")
@@ -10 +11,2 @@ def main():
-    pass
+    run()
+    stop()
"""
parse_hunks(diff)
# [(1, 3, 1, 4), (10, 1, 11, 2)]
```
