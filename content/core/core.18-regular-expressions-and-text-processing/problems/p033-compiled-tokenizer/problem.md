# Compile once: a tokenizer with a master pattern

A **tokenizer** cuts text like `x = 3.5 + y2` into pieces called tokens:
`NAME x`, `OP =`, `NUMBER 3.5`, `OP +`, `NAME y2`. Calculators, config readers and
programming languages all start with one.

The classic regex trick is a single **master pattern**: one named group per token kind, joined
with `|`. After a match, `m.lastgroup` tells you **which** named group matched, so you know the
kind without any `if` chain. The pattern is compiled **once**, in `__init__`, and reused for every
text.

Write a class `Tokenizer` in `solution.py`.

- `__init__(self)` stores the compiled master pattern in `self.pattern` (a `re.Pattern`) with
  these named groups, tried in this order:

  | Group | Matches |
  |---|---|
  | `NUMBER` | digits, optionally followed by `.` and more digits: `7`, `42`, `3.5` |
  | `NAME` | a letter or `_`, then any letters, digits or `_`: `x`, `y2`, `_tmp` |
  | `OP` | one of `+ - * / = ( )` |
  | `SKIP` | a run of whitespace (spaces, tabs, newlines) |
  | `MISMATCH` | any other single character |

- `tokens(self, text)` is a **generator** that yields `(kind, value)` tuples, left to right.
  - `SKIP` matches are not yielded.
  - A `MISMATCH` raises `ValueError` with a message that contains the bad character and its
    index, for example `unexpected character '$' at index 2`.
  - Tokens before the bad character are still yielded first (it is a generator).

**Example**

```python
t = Tokenizer()
list(t.tokens("x = 3.5 + y2"))
# [('NAME', 'x'), ('OP', '='), ('NUMBER', '3.5'), ('OP', '+'), ('NAME', 'y2')]

list(t.tokens("12abc"))
# [('NUMBER', '12'), ('NAME', 'abc')]

list(t.tokens("3 $ 4"))
# ValueError: unexpected character '$' at index 2
```
