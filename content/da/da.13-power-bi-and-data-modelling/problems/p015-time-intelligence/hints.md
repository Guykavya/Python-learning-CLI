## Hint 1

Which function returns "the same dates one year earlier", and which "January 1 up to the last visible date"? Both are filter arguments of `CALCULATE`. For the percentage, what is the numerator and what is the denominator?

## Hint 2

```text
"Revenue PY": "CALCULATE([Revenue], SAMEPERIODLASTYEAR(Date[Date]))"
"Revenue YTD": "CALCULATE([Revenue], DATESYTD(Date[Date]))"
"YoY %": "DIVIDE([Revenue] - [Revenue PY], [Revenue PY])"
```
