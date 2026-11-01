## Approach

The model answer is in `answer.md`. The key is to keep two levels apart:

| Level | Who protects it | Example |
|---|---|---|
| One bytecode, interpreter internals | the GIL (or per-object locks in free-threaded builds) | reference counts, a single `list.append` |
| Several steps of **your** logic | **you**, with a `Lock` | `counter += 1`, check-then-act, read-then-write |

And two reasons a thread gives up the GIL: it **blocks** on I/O or sleep (voluntary), or the
**switch interval** expires while others wait (forced). The first is why I/O threads overlap;
the second is why your multi-step code can be cut in the middle.

## Check your answer

- Did you say the GIL protects the interpreter, not your program's logic?
- Did you name the gap between the load and the store in `counter += 1`?
- Did you mention the switch interval (about 5 ms) or "between bytecodes"?
- Did you explain that waiting releases the GIL, so I/O threads overlap?
- Did you name the free-threaded builds (3.13t/3.14t) and `sys._is_gil_enabled()`?
- Did you say races get **more** likely, not less, without the GIL?

## Another way

Prove it instead of arguing. Run 8 threads that each do
`v = counter; time.sleep(0); counter = v + 1` 1,000 times. `sleep(0)` forces a switch right
in the gap, and the total comes out far below 8,000 every time. Then add a `Lock` around the
three lines and it is exactly 8,000. (p006 does this.)
