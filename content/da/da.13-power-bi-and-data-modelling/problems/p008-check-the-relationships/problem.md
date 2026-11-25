# Check the relationships

Chapter section 4.7. A model can be built and still be wrong: a relationship whose **one side** is not unique, a fact with **blank** or **orphan** keys, a filter direction set to **both** without a reason, an **inactive** relationship that no measure uses. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

`m` is a `Model` (the chapter's engine). Its tables are in `m.t` (a dict of DataFrames) and its relationships in `m.rels`; each relationship `r` has `r.many`, `r.mcol` (the foreign key), `r.one`, `r.ocol` (the key), `r.active` and `r.both`.

Write `check_relationships(m)`. It returns a DataFrame with **one row per relationship** (in the order of `m.rels`) and these columns:

| column | content |
|---|---|
| `relationship` | `"Sales[ProductKey] -> Product[ProductKey]"` (many side -> one side) |
| `one side unique` | `True` if the one-side column has no duplicates |
| `blank keys` | the number of missing values in the many-side column (an int) |
| `orphan rows` | the number of **non-blank** many-side keys that are not in the one-side column (an int) |
| `direction` | `"both"` if `r.both`, else `"single"` |
| `active` | `r.active` |

## Example

A sale with `ProductKey = 99` that is not in `Product` gives `orphan rows = 1` for `Sales[ProductKey] -> Product[ProductKey]`, and a relationship built with `both=True` shows `direction = both`.
