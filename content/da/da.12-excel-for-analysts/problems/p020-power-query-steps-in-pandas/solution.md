## Approach

Every Power Query step has a pandas twin (the dictionary of section 9.4). A list of small dicts describes the whole query as **data**, which can be tested, logged and compared; the function just plays it back.

## Code

```python
import pandas as pd


def apply_steps(df, steps):
    out = df.copy()
    for s in steps:
        name = s["step"]
        if name == "trim":
            for c in s["columns"]:
                out[c] = out[c].str.strip()
        elif name in ("lower", "upper", "proper"):
            for c in s["columns"]:
                out[c] = getattr(out[c].str, {"lower": "lower", "upper": "upper", "proper": "title"}[name])()
        elif name == "replace":
            out[s["column"]] = out[s["column"]].str.replace(s["old"], s["new"], regex=False)
        elif name == "change_type":
            for c, kind in s["types"].items():
                if kind == "date":
                    out[c] = pd.to_datetime(out[c], format="%Y-%m-%d", errors="coerce")
                else:
                    num = pd.to_numeric(out[c], errors="coerce")
                    out[c] = num.astype(int) if kind == "int" and num.notna().all() else num
        elif name == "filter_blanks":
            col = out[s["column"]]
            out = out[col.notna() & (col.astype(object) != "")]
        elif name == "unpivot":
            out = out.melt(id_vars=s["id_columns"], var_name=s["var_name"], value_name=s["value_name"])
        elif name == "group":
            out = out.groupby(s["by"], as_index=False).agg(**s["aggregations"])
        else:
            raise ValueError(f"unknown step: {name}")
    return out.reset_index(drop=True)
```

## Complexity

O(rows x steps).

## Another way

`DataFrame.pipe(step_function, ...)` chains functions; a list of dicts is better when the steps come from a file or must be logged.
