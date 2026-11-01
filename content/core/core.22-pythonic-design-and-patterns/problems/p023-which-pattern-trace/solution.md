## Approach

Follow the counter value and the two watchers (W1 logs every change, W2 prints `big!` when the
new value is 10 or more). The names `do`/`undo` only call `set`, so every undo also notifies
the watchers.

## Trace

| Step | Counter set to | W1 prints | W2 prints |
|---|---|---|---|
| `Add 4`.do | `0 + 4 = 4` | `log: 0 -> 4` | nothing (4 < 10) |
| `Add 7`.do | `4 + 7 = 11` | `log: 4 -> 11` | `big!` |
| `Add -2`.do | `11 - 2 = 9` | `log: 11 -> 9` | nothing |

`print("value:", 9)` gives `value: 9`.

Strategies on 9 (they are only called, nothing is observed): `double` gives `18`, `negate`
gives `-9`, the lambda gives `10`. So the lines are `double 18`, `negate -9`, `lambda 10`.

Undo loop: `done` has three commands; the loop runs while `len(done) > 1`.

| Step | Counter set to | W1 | W2 |
|---|---|---|---|
| pop `Add -2`.undo | `9 - (-2) = 11` | `log: 9 -> 11` | `big!` |
| pop `Add 7`.undo | `11 - 7 = 4` | `log: 11 -> 4` | nothing |

Now `len(done)` is 1, so the loop ends. `counter.watchers.pop(0)` removes W1 (the logger), so only
W2 is left. `done[0].undo()` sets `4 - 4 = 0`: W2 sees `0 >= 10` is false and prints nothing.
`final: 0`.

## Another way

Print the value *inside* a watcher to see the same sequence; or run the program with a
`breakpoint()` inside `Counter.set` and watch `old`, `value` and `self.watchers`.
In real code an undo that changes state silently (without notifying observers) would leave the
UI out of date, which is why undo goes through the same `set`.
