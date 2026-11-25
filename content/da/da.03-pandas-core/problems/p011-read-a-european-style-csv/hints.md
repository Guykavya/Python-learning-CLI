## Hint 1

Read the first row of the file as the computer would with all defaults: what would the separator be, and what would `1.250,50` become? Which `read_csv` parameter fixes each of the four differences (separator, decimal mark, thousands mark, missing marker), and which two handle the date?

## Hint 2

```text
pd.read_csv(path,
            sep=";",
            decimal=",",
            thousands=".",
            na_values=["-"],
            parse_dates=["date"],
            date_format="%d.%m.%Y")
```
