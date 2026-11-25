## Model answer

**Excel.** `XLOOKUP` and `VLOOKUP` (exact match) return the **first** matching row. All 120 lines of `P05` get the cost 24.00. The second row (29.00) is never used, and nothing warns you: the lookup has no way to say "this key was not unique".

**pandas.** `merge(..., how="left")` keeps **every** match. Each of the 120 `P05` lines meets two rows, so the result has 240 rows for `P05`: a **fan-out**. Every sum over the order lines (revenue, units) now counts those lines twice. With `validate="m:1"` pandas raises a `MergeError` because the right table is not unique on the key,
which is the right behaviour: the problem is stopped before it reaches a total.

**The totals.** The Excel cost for `P05` is 120 x 24.00 = 2,880 (and revenue is right); the merge gives revenue and units for `P05` counted twice and a cost of 120 x 24 + 120 x 29 = 6,360. Neither is right: the lookup hides the second price, the merge duplicates the lines. Which cost applies depends on the **order date** (a price change has a start date).

**Before the lookup.** Check that the key is unique (`COUNTIF` > 1 in Excel, `duplicated()` / `validate="m:1"` in pandas), decide which row is valid for each order (add the validity dates and look up by code **and** date, or keep the latest row and say so), and add a control total: the number of lines and the revenue must be the same before and after the join.

**Checklist: your answer should mention**
- [ ] a lookup returns the first match and ignores the other duplicate silently
- [ ] a left join keeps all matches: the order lines are duplicated (fan-out)
- [ ] validate="m:1" (or a COUNTIF uniqueness check) stops the problem early
- [ ] neither total is right until you decide which price applies (dates)
- [ ] control totals before and after the join
