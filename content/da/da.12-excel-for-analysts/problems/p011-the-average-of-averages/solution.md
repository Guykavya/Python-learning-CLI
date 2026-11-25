## Approach

The first formula weights lines equally; the second weights units equally (it is a ratio of two sums). When line sizes vary, the two differ, and the second is usually the one a finance question means.

## Code

```python
def add_price_metrics(wb, region):
    ws = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    ws["A1"], ws["B1"] = "Average line price", f'=AVERAGEIFS(Price,Region,"{region}")'
    ws["A2"], ws["B2"] = "Revenue per unit", f'=SUMIFS(Rev,Region,"{region}")/SUMIFS(Units,Region,"{region}")'
    return ws
```

## Complexity

O(1) to write; the evaluation is O(rows).

## Another way

In pandas: `df.groupby("region")["unit_price"].mean()` against `df.groupby("region")["revenue"].sum() / df.groupby("region")["units"].sum()`: the same two numbers.
