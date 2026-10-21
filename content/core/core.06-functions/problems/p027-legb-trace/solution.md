## Walkthrough

- In `outer`, `inner` assigns `x`, so `inner`'s `x` is local: `L`. That does not affect
  `outer`'s `x`, which is still `E`.
- In `read_outer`, `inner` only reads `x`; there is no local, so the **enclosing** `x`, `E2`, is
  found.
- `read_global` has no local `x` and no enclosing function, so it finds the global `G`.
- `shadow` assigns `len = 3`, a local that hides the built-in only inside `shadow`.
- At module level, `x` is still `G` (no function used `global`), and `len` is still the built-in.

## The exact output

```text
inner: L
outer: E
read: E2
global: G
shadow: 3
module: G 3
```
