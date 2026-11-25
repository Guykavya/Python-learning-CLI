import numpy as np
import pandas as pd


def retention_matrix(orders, customers, asof):
    asof = pd.Timestamp(asof)
    cu = customers.assign(cohort=customers["first_order"].dt.to_period("M"))
    size = cu.groupby("cohort").size()
    o = orders[orders["order_date"] <= asof].merge(cu[["customer_id", "cohort"]], on="customer_id", validate="m:1")
    om = o["order_date"].dt.to_period("M")
    o["k"] = (om.dt.year - o["cohort"].dt.year) * 12 + (om.dt.month - o["cohort"].dt.month)
    last = asof.to_period("M")
    max_k = pd.Series({c: (last.year - c.year) * 12 + (last.month - c.month) for c in size.index})
    active = o.groupby(["cohort", "k"])["customer_id"].nunique().unstack("k")
    ks = list(range(int(max_k.max()) + 1))
    active = active.reindex(index=size.index, columns=ks).fillna(0.0)
    m = active.div(size, axis=0)
    for c in m.index:
        m.loc[c, [k for k in ks if k > max_k[c]]] = np.nan
    return m
