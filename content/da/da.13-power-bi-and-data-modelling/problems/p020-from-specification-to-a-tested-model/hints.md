## Hint 1

Split the work: first read and build (tables, relationships, measures), then think about the checks. For the field `Sales[OrderDateKey]`, how do you get the table and the column out of the text? Remember that `Model.relate` raises an error when the one side is not unique.

## Hint 2

```text
many, mcol = r["from"][:-1].split("["); one, ocol = r["to"][:-1].split("[")
try: m.relate(many, mcol, one, ocol, active=r.get("active", True), both=(r.get("direction") == "both"))
except Exception as e: raise ValueError(f"relationship {r['from']} -> {r['to']}: {e}") from None
fields: t, c = f.split("["); exists = t in model.t and c[:-1] in model.t[t].columns
```
