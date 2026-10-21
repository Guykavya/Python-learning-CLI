# Describe an exception object

A program logs every error it handles as one short line. Write `describe_error(err)` that takes
an **exception object** (already created, possibly already caught) and returns that line:

1. No arguments (`err.args` is empty): just the type name, for example `"ValueError"`.
2. A `KeyError`: `"KeyError: missing key <key>"`, where `<key>` is the key itself, `err.args[0]`,
   converted with `str()`. Do **not** use `str(err)` here: section 7 explains why it adds quotes.
3. Any other exception: `"<TypeName>: <args>"`, where `<args>` is every argument converted
   with `str()` and joined with `", "`.

The type name comes from `type(err).__name__`.

**Examples**

```python
describe_error(ValueError("age must be positive"))   # 'ValueError: age must be positive'
describe_error(ValueError())                         # 'ValueError'
describe_error(KeyError("cake"))                     # 'KeyError: missing key cake'
describe_error(KeyError(42))                         # 'KeyError: missing key 42'
describe_error(ValueError("bad row", 3))            # 'ValueError: bad row, 3'

try:
    1 / 0
except ZeroDivisionError as e:
    describe_error(e)                                # 'ZeroDivisionError: division by zero'
```
