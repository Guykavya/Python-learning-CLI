# Call every function in a list

Write `call_all(funcs, value)` that calls each function in the list `funcs` with `value` and
returns a list of the results, in the same order.

Then define a module-level list `CHECKS = [len, str.upper, str.isdigit]` (the functions
themselves) and write `describe(value)` that returns `call_all(CHECKS, value)`.

**Examples**

```python
call_all([abs, str], -4)           # [4, '-4']
call_all([], 10)                   # []
CHECKS                             # [len, str.upper, str.isdigit]
describe("abc")                    # [3, 'ABC', False]
describe("2026")                   # [4, '2026', True]
```
