# Code object facts

When Python runs a `def` statement it does not keep your source text. It keeps a **code
object**: the compiled bytecode plus tables the bytecode refers to. Every function has one in
`func.__code__`. The tables have stable names that are the same on every Python from 3.11 on:

| Attribute | What it holds |
|---|---|
| `co_name` | the function's name (`"<lambda>"` for a lambda) |
| `co_argcount` | how many **positional** parameters (not `*args`, not keyword-only, not `**kwargs`) |
| `co_varnames` | names of all local variables, parameters first |
| `co_names` | other names the bytecode uses: globals, built-ins **and attribute names** like `append` |
| `co_consts` | the literal constants the bytecode loads (may include `None`) |

Copy `starter.py` to `solution.py` and write `code_facts(func)`. It returns a dict with exactly
these five keys:

- `"name"`: `co_name`
- `"argcount"`: `co_argcount`
- `"locals"`: the names in `co_varnames`, **sorted**
- `"names"`: the names in `co_names`, **sorted**
- `"constants"`: a list of the items of `co_consts`, in their original order, **without `None`**

**Example**

```python
RATE = 0.18

def price_with_tax(price, qty):
    subtotal = price * qty
    tax = subtotal * RATE
    return round(subtotal + tax, 2)

facts = code_facts(price_with_tax)
facts["name"]        # 'price_with_tax'
facts["argcount"]    # 2
facts["locals"]      # ['price', 'qty', 'subtotal', 'tax']
facts["names"]       # ['RATE', 'round']
```

Why sorted, and why drop `None`? The *order* of `co_varnames` after the parameters, and whether
`None` (or a small int) sits in `co_consts`, are compiler details that changed between 3.11 and
3.14. The set of names does not. Only rely on what the language keeps stable.
