## Approach

The date filters of `CALCULATE` replace the visual's date filter by a shifted or extended set of dates; the facts follow through the relationship. The percentage is a plain `DIVIDE` of two measures, so it is blank when last year is blank.

## Code

```python
TIME_MEASURES = {
    "Revenue PY": "CALCULATE([Revenue], SAMEPERIODLASTYEAR(Date[Date]))",
    "Revenue YTD": "CALCULATE([Revenue], DATESYTD(Date[Date]))",
    "YoY %": "DIVIDE([Revenue] - [Revenue PY], [Revenue PY])",
}
```

## Complexity

O(rows) per evaluation.

## Another way

`DATEADD(Date[Date], -1, YEAR)` shifts by a stated interval and also works for months or quarters (for example "revenue prior month").
