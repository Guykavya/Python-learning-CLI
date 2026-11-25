## Model answer

**1. SUM skips text.** Excel adds 10 + 5 + 3.5 = **18.5** and skips the text `"7"` (and the blank), without a warning. In pandas, `pd.to_numeric(s, errors="coerce").sum()` converts `"7"` to 7 first and gives **25.5**; a plain `s.sum()` on the object column
would try to add numbers and text and raise an error or concatenate. A column of numbers stored as text therefore gives Excel totals that are too small.

**2. AVERAGE ignores blanks, not zeros.** `AVERAGE` of 10, 5, blank, 3.5 is (10 + 5 + 3.5) / 3 = **6.17**. A pandas column read with the blank filled with 0 (`fillna(0)`) gives (10 + 5 + 0 + 3.5) / 4 = **4.63**. `Series.mean()` also skips NaN, so it matches Excel only if
the blank was kept as NaN; the difference between "missing" and "zero" decides the number.

**3. ROUND goes away from zero.** `ROUND(2.5, 0)` is **3** and `ROUND(-2.5, 0)` is **-3**. Python's `round(2.5)` and `Series.round()` use round-half-to-even and give **2** (and -2); `round(3.5)` is 4 in both.

**4. Criteria are case-insensitive but exact about spaces.** `SUMIFS(..., "North")` includes the rows `North` and `north`, but not `"North "`. In pandas, `df[df["region"] == "North"]` is case-sensitive and gives a smaller sum (it misses `north`);
it also misses `"North "`, the same as Excel.

**Checklist: your answer should mention**
- [ ] SUM skips text numbers (18.5 against 25.5 after conversion)
- [ ] a blank is not 0 in AVERAGE (6.17 against 4.63 with fillna(0))
- [ ] ROUND half away from zero against Python's half to even
- [ ] case-insensitive criteria in Excel against case-sensitive == in pandas, and the trailing-space trap
- [ ] neither tool is wrong: they follow different rules
