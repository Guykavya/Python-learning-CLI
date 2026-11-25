# Excel rules a pandas user must know

Chapter section 4.2. The same-looking formula in Excel and the same-looking expression in pandas can give **different numbers**, and neither is "wrong": they follow different rules.

In `answer.md`, for **each of these four rules**, state the rule and give the **pandas expression** that would give a *different* number on the same data (and what that number would be on the small example). About 250 to 350 words.

1. `SUM` over a range **skips text** (a number stored as text, like `"7"`, is not added).
2. `AVERAGE` over a range **ignores blank cells**, but a cell containing `0` counts.
3. `ROUND(2.5, 0)` is **3** (halves go away from zero), and `ROUND(-2.5, 0)` is `-3`.
4. `SUMIFS(units, region, "North")` matches `"north"` as well as `"North"` (**case-insensitive**), but not `"North "` with a trailing space.

Use this small column for rule 1 and 2: `10`, `5`, `"7"` (text), blank, `3.5`.

## Example

A start for rule 1: "Excel's SUM gives 18.5 because the text `"7"` is skipped. In pandas, `pd.to_numeric(pd.Series([10, 5, "7", None, 3.5]), errors="coerce").sum()` gives 25.5, because pandas converts the text first..."
