## Approach

Compute the fences once from all values, then build four versions of the Series and summarise each with the same helper.
`s.clip(lo, hi)` pulls every value into the fences, and `s.where(~flags, s.clip(lo, hi))` keeps the original where
the flag is `False` and uses the clipped value where it is `True`. That is exactly "flagged values only".

## Code

```python
def outlier_strategies(s, flags):
    q1, q3 = s.quantile([0.25, 0.75])
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    flags = flags.fillna(False).astype(bool)

    def stat(x):
        return {"mean": float(x.mean()), "median": float(x.median())}

    out = {
        "keep": stat(s),
        "remove": stat(s[~flags]),
        "cap": stat(s.where(~flags, s.clip(lo, hi))),
        "flag_only": stat(s),
    }
    out["flag_only"]["n_flagged"] = int(flags.sum())
    return out
```

## Complexity

O(n log n) for the quantiles (a sort), O(n) for everything else.

## Another way

Winsorising at percentiles (`s.clip(*s.quantile([.01, .99]))`) caps **every** value outside the percentiles, flagged
or not, and rewrites honest values (chapter 6.5). Capping only the flagged values is the more careful version: the
rule decides who is a suspect, the cap only limits their influence. Notice that `"keep"` and `"flag_only"` give the
same numbers: flagging alone changes nothing until you act on the flag.
