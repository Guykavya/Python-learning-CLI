# Dates are numbers

Chapter section 2.2. Inside Excel a date is a **number**: the count of days since a starting day, and a time of day is the **fraction of a day** (0.5 is noon). That is why `=B2+30` adds 30 days. For dates from **1 March 1900** on, the serial number is the number of days since **30 December 1899**. (Excel counts 1 January 1900
as day 1 and keeps a fake 29 February 1900, a bug from an older program, so the count is one day off before March 1900. You do not need to handle those early dates.)

Write two functions without using `openpyxl`:

- `to_serial(d)`: a `datetime.datetime` or `datetime.date` -> the Excel serial number as a float (a `date` is midnight);
- `from_serial(n)`: a number -> the `datetime.datetime` it stands for (the fraction is the time of day).

## Example

```python
to_serial(datetime(2024, 3, 15))            # 45366.0
to_serial(datetime(2024, 3, 15, 12, 0))     # 45366.5
from_serial(45366.25)                       # datetime(2024, 3, 15, 6, 0)
```
