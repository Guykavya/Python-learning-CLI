## Hint 1

What do you need per stratum: a count or a mean? Which checks must run before you compute anything, and in which situations is the result not defined?

## Hint 2

```text
check sum(shares) is 1 ; check every sample stratum is in pop_shares ; check every pop stratum has rows
means = sample_df.groupby(by)[value].mean()
return sum(share * means[s] for s, share in pop_shares.items())
```
