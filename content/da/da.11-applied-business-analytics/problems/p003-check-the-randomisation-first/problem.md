# Check the randomisation first

Chapter section 2.4. If a test is planned as a 50/50 split but the groups come out 12,000 and 11,100, something went wrong **before** the analysis (a bug in assignment, bots, a broken tracking tag),
and no comparison of A and B can be trusted. This is a **sample ratio mismatch** (SRM). We test it with a chi-square test of the group counts against the planned shares.

Write two functions:

- `srm_check(counts, expected_share=(0.5, 0.5))`: returns `(chi2, p)` as plain floats from a chi-square goodness-of-fit test (`scipy.stats.chisquare`) of `counts` against `sum(counts) * share` for each group.
- `srm_verdict(counts, expected_share=(0.5, 0.5))`: returns the string `"MISMATCH"` when `p < 0.001` and `"ok"` otherwise. (The threshold is strict on purpose: with large samples we only want to stop for a real problem.)

If `expected_share` does not add up to 1 (within 1e-9), raise `ValueError("shares must add up to 1")`.

## Example

`srm_verdict([12_000, 11_100])` is `"MISMATCH"` (chi-square 35.1, p about 3e-9). A 50/50 test with 12,010 and 11,990 is `"ok"`.
