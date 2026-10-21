## Hint 1

List the steps and, for each, how it can fail: by an exception (which one?) or by quietly giving
a strange value (which test catches that?).

## Hint 2

`0 ** -1` is `1 / 0` in disguise: what does it raise? `1 / 1e-320` is a huge but finite number or
inf? Try both. A helper `to_number(text)` that returns a finite float or `None` keeps the main
function readable.

## Hint 3

```
if not str: raise TypeError
parts = expression.split(); if len != 3: return SHAPE
a = to_number(first) / b = to_number(third): return "not a number" for the first that is None
if op not in OPERATIONS: return unknown operator
try: result = OPERATIONS[op](a, b)
except ZeroDivisionError: ...
except OverflowError: ...
if isinstance(result, complex): ...
if not math.isfinite(result): ...
return str(result)
```
