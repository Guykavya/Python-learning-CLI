## Hint 1

Keep two running totals on paper, `setup` and `stmt`, and never reset them: `log` is shared by
every call. For each `timeit(...)` call ask: how many times does setup run (one) and how many
times does stmt run (`number`)? What changes when `number=0`?

## Hint 2

`repeat(repeat=3, number=4)` is three separate `timeit(number=4)` calls, so the setup runs once
for **each** of them. For the string examples, the setup `data.clear()` empties the list at the
start of every timing. For the `gc` lines: off inside the timed loop, unless the setup turns it
back on; back on after `timeit` returns.

```
timeit(n):          setup += 1, stmt += n
repeat(r, n):       setup += r, stmt += r * n, returns a list of r floats
string with clear:  list holds only what the LAST timing appended
```
