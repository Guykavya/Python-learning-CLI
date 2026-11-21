## Hint 1

Line 1: what does `/` do when the right-hand side is an **absolute** path? Lines 2, 3 and 5: `suffix` is only the **last** dot-part, `stem` is the name without that last suffix. Line 4: does `Path.glob("*")` skip names starting with a dot, and does `*` go into subfolders?

## Hint 2

Line 6 has two comparisons. Pure path operations never remove `..`: `base / ".." / "secret.txt"` keeps the `..` as a part, so it is a **different path** from `folder / "secret.txt"` even though both name the same file. `resolve()` asks the file system and collapses `..` (and symlinks), so after resolving both sides agree. That is exactly why `is_inside` resolves before comparing.
