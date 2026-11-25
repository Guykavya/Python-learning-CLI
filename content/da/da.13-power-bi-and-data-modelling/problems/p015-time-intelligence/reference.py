TIME_MEASURES = {
    "Revenue PY": "CALCULATE([Revenue], SAMEPERIODLASTYEAR(Date[Date]))",
    "Revenue YTD": "CALCULATE([Revenue], DATESYTD(Date[Date]))",
    "YoY %": "DIVIDE([Revenue] - [Revenue PY], [Revenue PY])",
}
