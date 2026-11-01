## Hint 1

Run the table through the starter and list the rows that differ. What do they have in common
(weights exactly on a limit? prices with a third decimal?). Then look for two things the
table cannot show: does the function change what the caller passed in? Does a call affect a
*later* call? Try: price a 30 kg parcel, then a 2 kg parcel, and print both.

## Hint 2

The four changes, as questions:

```
1. "if weight_kg < limit"  vs the documented "limits are inclusive"          -> which operator?
2. "int(total * 100) / 100" vs "ROUNDED to 2 decimals"                       -> which function?
3. extras.append("insured") changes the caller's list                        -> work on a copy
4. extras=[] is created once, so the 'insured' added by a heavy parcel stays -> default None
```

A good fix for 3 and 4 together: `names = set(extras or ())` and add `"insured"` to `names`.
