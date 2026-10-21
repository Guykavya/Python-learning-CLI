## Walkthrough

The default list is created once. Calls 1, 2 and 4 append to it, so its length goes 1, 2, then
3; call 3 passes its own empty list, so it reports length 1 and leaves the default alone.
`count` is an int: `count += 1` rebinds a local name, so it is always `0 + 1 = 1`, or `10 + 1 = 11`
when `count=10` is passed. The last print of `__defaults__` shows the shared list holding `a`, `b`
and `d`, and the int default still `0`.

`start` never changes a default: `None` is falsy, so `seen or ["start"]` builds a new list each
call. But `mine` is an empty list, also falsy, so `start("z", mine)` replaces it with a new list
and the caller's `mine` stays empty. That is why `is None` is the right test.

## The exact output

```text
([], 0)
(1, 1)
(2, 1)
(1, 1)
(3, 11)
(['a', 'b', 'd'], 0)
['start', 'x']
['start', 'y']
['start', 'z'] []
```
