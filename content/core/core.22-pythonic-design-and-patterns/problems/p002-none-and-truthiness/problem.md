# None, truthiness and the zero that vanished

`starter.py` has three helpers from a settings tool. They use two lazy habits:

- `if not value:` as a shortcut for "is it missing?". But `0`, `""`, `[]` and `False` are all
  *falsy* and all perfectly valid values. A port of `0` or a name of `""` vanishes.
- `value == None`, `value == True`, `value == False`. `None`, `True` and `False` are
  singletons: test them with `is`. And `1 == True` is `True` in Python, so `describe(1)` says "yes".

Copy `starter.py` to `solution.py` and fix the three functions. Keep names and parameters.

**describe(value)** returns:

| value | result |
|---|---|
| `None` | `"missing"` |
| `True` | `"yes"` |
| `False` | `"no"` |
| `0` or `0.0` | `"zero"` |
| `""` | `"empty text"` |
| `[]` | `"empty list"` |
| anything else | `"value "` + `repr(value)` |

**first_non_empty(values, default=None)** returns the first item that **is not `None`**
(so `0`, `""`, `[]` and `False` count), or `default` if there is none.

**config_get(config, key, default)** returns `config[key]`, unless the key is missing **or its
value is `None`**: then return `default`. A stored `0`, `""`, `False` or `[]` is a real answer.

Your file is also checked: no `== None`, `== True`, `== False` (or `!=`).

**Example**

```python
describe(0)                          # 'zero'      (the starter says 'empty')
describe(1)                          # 'value 1'   (the starter says 'yes')
first_non_empty([None, 0, 5])        # 0           (the starter returns 5)
config_get({"port": 0}, "port", 80)  # 0           (the starter returns 80)
```
