## Walkthrough

- `"4"`: `try` succeeds, so `else` prints `else 4`, then `finally`, then `end 4`.
- `"x"`: `ValueError` is handled; `except` sets `number = 0`; `else` is skipped; `finally` runs;
  the function continues after the statement and prints `end 0`.
- `"-2"`: like `"4"`. The total is `4 + 0 + (-2) = 2`.
- `None`: `int(None)` raises `TypeError`. No `except` clause matches, so `else` is skipped and
  `finally` runs while the exception is pending. Then the exception propagates: `end` is never
  printed and nothing is returned. The caller's `try` catches it.

## The exact output

```text
start '4'
  else 4
  finally
  end 4
start 'x'
  except
  finally
  end 0
start '-2'
  else -2
  finally
  end -2
total 2
start None
  finally
TypeError reached the caller
```
