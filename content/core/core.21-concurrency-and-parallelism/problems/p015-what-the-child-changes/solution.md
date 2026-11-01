## Approach

Track each process separately, with its own `items`.

| Step | Process | What happens | Printed |
|---|---|---|---|
| 1 | parent | top level runs, `items = ['start']` | `loading module as __main__` |
| 2 | parent | inside the guard: append `'parent'` | `parent before ['start', 'parent']` |
| 3 | child 1 | new interpreter imports the script as `__mp_main__`: top level runs, its own `items = ['start']`; the guard is false | `loading module as __mp_main__` |
| 4 | child 1 | `child("one")` appends to the **child's** list | `child sees ['start', 'one']` |
| 5 | parent | `join()` returned; target returned normally | `exit code 0` |
| 6 | parent | the child's append happened in another memory | `parent after ['start', 'parent']` |
| 7 | parent | `child("main")` is a normal call **in the parent** | `child sees ['start', 'parent', 'main']` |
| 8 | parent | | `parent now ['start', 'parent', 'main']` |
| 9 | child 2 | fresh import again: `['start']` only, not the parent's current list | `loading module as __mp_main__` |
| 10 | child 2 | | `child sees ['start', 'two']` |
| 11 | parent | still unchanged by any child | `parent end ['start', 'parent', 'main']` |

Lessons:

- Changes made **in a child** never come back to the parent. To get results back, return them
  through a pool (`ProcessPoolExecutor`), a `multiprocessing.Queue`, or shared memory (p014).
- With spawn, the child does **not** see what the parent did after start-up (`'parent'`,
  `'main'`); it only sees what the import builds, plus the arguments you pass.
- Top-level code runs again in every spawned child. That is why the
  `if __name__ == "__main__":` guard is required: without it, each child would start
  processes of its own. (Python detects this and raises `RuntimeError`.)
- `exitcode` is `0` after a normal return, `1` if the target raised, and negative (`-N`) if the
  process was killed by signal `N` (Linux/macOS).

**With the "fork" start method** (Linux only, and no longer the default in 3.14), the child is
a copy of the parent at the moment of `start()`: the module is not imported again, so
`loading module as __mp_main__` is not printed, and the children see
`['start', 'parent', 'one']` and `['start', 'parent', 'main', 'two']`. The parent's own lines
are the same: a fork child still changes only its copy.

## Output

```text
loading module as __main__
parent before ['start', 'parent']
loading module as __mp_main__
child sees ['start', 'one']
exit code 0
parent after ['start', 'parent']
child sees ['start', 'parent', 'main']
parent now ['start', 'parent', 'main']
loading module as __mp_main__
child sees ['start', 'two']
parent end ['start', 'parent', 'main']
```
