## Approach

`work()`:

1. `with section("a")` prints `enter a`. The yielded value is `'A'`, so `got A`.
2. The inner `with section("b", swallow=KeyError)` prints `enter b` and `got B`.
3. `{}["x"]` raises `KeyError`. It is thrown into `section("b")` at the `yield`. The `except swallow` clause
   matches, prints `swallowed KeyError`, and `finally` prints `exit b`. Because the generator handled the
   error, the `with` statement **swallows** it. The line `not printed` is skipped, but the code after the inner
   `with` runs: `after b`.
4. `return "done"` leaves the outer `with`. The `finally` of `a` runs on the way out: `exit a`.
   Only then does `print(work())` print `done`.

Section `c`:

5. `enter c`, `in c`. `ValueError` is thrown into the generator, but `except KeyError` does not match.
   `finally` runs (`exit c`) and the error goes on out of the `with`. The outer `except ValueError` prints
   `outer caught bad`. The stderr line is not shown.
6. `end`.

## Output

```text
enter a
got A
enter b
got B
swallowed KeyError
exit b
after b
exit a
done
enter c
in c
exit c
outer caught bad
end
```

## Complexity

Not applicable.

## Another way

Remove `finally` and put `print("exit", name)` after the `yield`. Run the program again. The `exit` lines for
the sections that fail or return are missing. That is why cleanup in a context manager belongs in `finally`.
