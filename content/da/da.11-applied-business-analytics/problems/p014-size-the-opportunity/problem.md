# Size the opportunity

Chapter section 3.5. "Mobile loses a fifth of its carts at the checkout step" is a finding; "**fixing it is worth about N extra purchases a month**" is a decision. Write `opportunity(df, target_rate, n_boot=2000, seed=2)` for
a sessions table with the columns `device`, `added_to_cart`, `started_checkout` and `purchased` (booleans). Use only the **mobile** sessions:

- `carts`: number of mobile sessions with `added_to_cart`; `now_rate`: the share of those that `started_checkout`;
- `pay_rate`: among mobile sessions with `started_checkout`, the share that `purchased`;
- extra purchases a month if the cart-to-checkout rate rose to `target_rate`, with the later step unchanged: `max(target_rate - now_rate, 0) * carts * pay_rate`;
- the uncertainty: bootstrap the cart-to-checkout rate (`n_boot` resamples of the mobile carts with replacement, `numpy.random.default_rng(seed)`), compute the extra purchases for each, **never below 0**, and report the 2.5%, 50% and 97.5% quantiles.

Return a dict: `{"carts", "now_rate", "pay_rate", "low", "mid", "high"}` (plain numbers). If there are no mobile carts, raise `ValueError("no mobile carts")`.

## Example

1,000 mobile carts, 400 start checkout (now 40%), 300 of those buy (pay 75%), target 55%: the point estimate is `0.15 x 1,000 x 0.75 = 112.5` extra purchases.
