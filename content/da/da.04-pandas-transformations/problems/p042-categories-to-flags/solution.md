## Approach

`get_dummies(df, columns=[...])` keeps the other columns, removes the encoded one and appends one column per distinct
value, sorted, named `<prefix>_<value>`. In pandas 3 the flags are `bool` by default; `dtype=int` gives 0/1 integers.
It returns a new frame.

## Code

```python
import pandas as pd


def channel_flags(orders):
    return pd.get_dummies(orders, columns=["channel"], prefix="ch", dtype=int)
```

## Complexity

O(n × k) for n rows and k distinct channels.

## Another way

`pd.crosstab(orders.index, orders["channel"])` builds the same flags by counting, or by hand:
`orders.assign(ch_online=(orders["channel"] == "online").astype(int))` per value. For a model, pass
`drop_first=True` to remove one column that the others determine.
