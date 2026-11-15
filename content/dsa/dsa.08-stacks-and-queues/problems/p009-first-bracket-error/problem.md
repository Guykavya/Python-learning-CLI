# Where is the first bracket error?

An editor wants to underline the first bracket problem in a line of code. Write `bracket_error(text)` that returns a tuple `(index, kind)`:

| Situation (scanning left to right) | Return |
|---|---|
| a closer arrives while **nothing** is open | `(index of that closer, "unexpected")` |
| a closer does not match the most recent open bracket | `(index of that closer, "mismatch")` |
| the scan ends with brackets still open | `(index of the EARLIEST bracket still open, "unclosed")` |
| everything is balanced | `(-1, "ok")` |

The first two are reported **as soon as they happen**, so an error in the middle wins over openers left at the end. Brackets are `()`, `[]`, `{}`; all other characters are ignored. Indices start at 0.

To know where an opener was, push `(bracket, index)` pairs (chapter section 5, "Where exactly is the error?").

## Example

```python
>>> bracket_error("([]{})")
(-1, 'ok')
>>> bracket_error("a(b]c")
(3, 'mismatch')
>>> bracket_error("()))")
(2, 'unexpected')
>>> bracket_error("{}((")
(2, 'unclosed')
>>> bracket_error("(()")
(0, 'unclosed')
```

In `"(()"` the bracket at index 1 is closed by index 2; the one at index 0 is never closed.

## Constraints

- `0 <= len(text) <= 10**5`.

## Think about

When the scan ends with several open brackets, where in your stack is the earliest one: at the top or at the bottom?
