## Hint 1

`groupby` sorts the groups by name: Delhi, Jaipur, Pune. Work out the count and the mean for each, then think about which jobs the direct mean averages over.

## Hint 2

```text
Delhi: 1 job (600)  Jaipur: 2 jobs (100, 200)  Pune: 4 jobs (100..400)
counts list [..], means list [..] in city order
simple mean of the means  = (600 + 150 + 250) / 3
weighted = (600*1 + 150*2 + 250*4) / 7 = direct mean = 1900 / 7
last line = simple mean minus direct mean
```
