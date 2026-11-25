## Hint 1

First the three plain numbers. Then, for the interval, resample the 0/1 column "started checkout" among the mobile carts. For each resample, the rate changes, and so do the extra purchases. Why clip at 0 inside the loop and not on the final quantiles?

## Hint 2

```text
m = df[df.device == "mobile"]; carts_df = m[m.added_to_cart]
chk = carts_df.started_checkout.to_numpy(float); now = chk.mean()
pay = m[m.started_checkout].purchased.mean()
rates = rng.choice(chk, (n_boot, len(chk))).mean(axis=1)
extra = clip(target - rates, 0, None) * carts * pay
low, mid, high = quantile(extra, [.025, .5, .975])
```
