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
