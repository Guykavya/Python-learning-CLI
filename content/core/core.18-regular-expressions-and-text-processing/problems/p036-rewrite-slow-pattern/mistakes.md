- Making it lazy: `(\w+?\s?)*` is just as slow. Lazy changes the **order** of the attempts, not
  how many there are.
- Dropping the `?`: `(\w+\s)*` is fast but rejects `"hello"` (a last word with no space after it).
- Using a single space `" "` instead of `\s`: then `"one\ttwo"` stops matching, but the original
  accepted tabs and newlines.
- Using `\s*` or `\s+`: that accepts `"hello  world"` with two spaces, which the original rejects.
- Using `re.match` without an end anchor: `match` only needs a prefix to match, so `"hi!"` would be
  accepted (the prefix `"hi"` matches). The tests use `fullmatch`; keep the pattern itself free of
  anchors.
- Testing the speed only on inputs that match. The explosion happens on near-misses that fail at
  the end.
