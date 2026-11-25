## Approach

The opportunity is a product of a gap (target minus now) and two volumes (carts, payment rate). The bootstrap shows how much the gap itself is uncertain, since "now" is estimated from a sample of carts.

## Code

```python
import numpy as np


def opportunity(df, target_rate, n_boot=2000, seed=2):
    m = df[df["device"] == "mobile"]
    carts_df = m[m["added_to_cart"]]
    if len(carts_df) == 0:
        raise ValueError("no mobile carts")
    chk = carts_df["started_checkout"].to_numpy(float)
    carts, now = len(chk), float(chk.mean())
    started = m[m["started_checkout"]]
    pay = float(started["purchased"].mean()) if len(started) else 0.0
    rng = np.random.default_rng(seed)
    rates = rng.choice(chk, (n_boot, carts)).mean(axis=1)
    extra = np.clip(target_rate - rates, 0, None) * carts * pay
    low, mid, high = np.quantile(extra, [0.025, 0.5, 0.975])
    return {"carts": int(carts), "now_rate": now, "pay_rate": pay, "low": float(low), "mid": float(mid), "high": float(high)}
```

## Complexity

O(n_boot x carts).

## Another way

Since `started_checkout` is 0/1, each bootstrap rate is `Binomial(carts, now) / carts`; `rng.binomial(carts, now, n_boot) / carts` gives the same distribution without building the matrix.
