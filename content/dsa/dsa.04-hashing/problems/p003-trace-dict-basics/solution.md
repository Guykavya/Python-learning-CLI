## Walkthrough

| statement | dictionary afterwards |
|---|---|
| `ages["ana"] = 30` | `{'ana': 30}` |
| `ages["ben"] = 25` | `{'ana': 30, 'ben': 25}` |
| `ages["ana"] = 31` | `{'ana': 31, 'ben': 25}` (update in place, same position) |
| `del ages["ben"]` | `{'ana': 31}` |
| `ages["dev"] = 40` | `{'ana': 31, 'dev': 40}` |
| `ages.pop("ana")` | returns 31, leaves `{'dev': 40}` |

## Output

```
{'ana': 31, 'ben': 25}
2
None
0
True False
ana 31
dev 40
[('ana', 31), ('dev', 40)]
31 {'dev': 40}
```

## Key ideas

- Assigning to an existing key replaces the value; the key keeps its place in the order.
- `.get` never raises; indexing a missing key raises `KeyError`.
- `in` tests **keys**, and string keys are case sensitive.
- Since Python 3.7 a `dict` remembers insertion order.
