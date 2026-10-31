## Hint 1

Which operations return a `Duration` and which return a plain number? Make a small table of the operand types for each operator.

## Hint 2

For `str`, use `divmod` twice: `hours, rest = divmod(total, 3600)` then `minutes, seconds = divmod(rest, 60)` and format with `:02d` for minutes and seconds.

## Hint 3

```
@total_ordering ; __init__: seconds must be int >= 0 else ValueError
of(cls, hours, minutes, seconds): cls(hours*3600 + minutes*60 + seconds)
__add__/__sub__: Duration only ; __sub__ negative -> ValueError
__mul__/__rmul__: int >= 0 ; __floordiv__: int > 0 -> Duration(self.s // n)
__truediv__: Duration only -> float
__eq__/__lt__/__hash__ on seconds ; __str__ H:MM:SS ; __repr__
```
