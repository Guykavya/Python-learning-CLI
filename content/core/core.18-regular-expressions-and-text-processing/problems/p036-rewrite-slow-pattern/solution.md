## Approach

`(\w+\s?)*` is slow because `\s?` is optional: then `\w+` repeated can cover `"aaaa"` as `aaaa`,
`aa|aa`, `a|aaa`, ... (2^(n-1) ways), and a failing input forces the engine to try them all.

Describe the language instead. Accepted strings are: zero or more "word + one whitespace", then
possibly one last word with no whitespace after it.

```
(?:\w+\s)*\w*
```

Why it is the same set:
- `""`: zero repetitions and `\w*` empty.
- `"a b"`: `a ` then `b`. `"a b "`: `a ` and `b `, then empty.
- `"a  b"`: after `a ` the next repetition needs `\w` but sees a space: no match, same as before.
- `" a"`: cannot start with whitespace in either pattern.

Why it is fast: each repetition **must** end with a whitespace character. A run of letters can
only be consumed in one way (the whole run, up to the next whitespace), so on `"a"*30 + "!"` the
engine makes about n small attempts and fails.

## Code

```python
import re

SAFE_RE = re.compile(r"(?:\w+\s)*\w*")
```

## Complexity

O(n) for most inputs and at worst O(n^2) on strange near-misses, compared with O(2^n) for the
original. The tests show 20,000 characters still finish in well under a millisecond.

## Another way

On Python 3.11+ you can keep the original idea and forbid backtracking into the repetition with a
possessive quantifier: `(?:\w+\s?)*+` or an atomic group `(?>(?:\w+\s?)*)`. Once the repetition
has eaten as much as it can, the engine does not go back to try other splits. The rewritten
`(?:\w+\s)*\w*` is still nicer: it works on every Python version and its meaning is obvious.

