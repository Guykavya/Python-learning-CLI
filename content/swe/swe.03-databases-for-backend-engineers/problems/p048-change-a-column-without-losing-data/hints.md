## Hint 1

Why not rename and convert in one step? What would the old application code (which still reads and writes `price`) do after a one-step change? Which step can be done while old code runs, and which must wait until all code has switched?

## Hint 2

Expand: add the new column, nullable, so nothing breaks. Migrate: copy the data over: `CAST(ROUND(price * 100) AS INTEGER)`; in a loop that updates a **limited** set of rows (`WHERE id IN (SELECT id ... LIMIT 500)`) until `rowcount` is 0. Contract: only then tighten and drop (batch mode on SQLite).

## Hint 3

```text
0002: batch add_column(price_paise, nullable)            | down: batch drop_column
0003: loop: UPDATE ... WHERE id IN (SELECT id ... price_paise IS NULL AND price IS NOT NULL LIMIT 500) until rowcount == 0 | down: SET price_paise = NULL
0004: batch: alter_column(price_paise, nullable=False); drop_column(price)   | down: add price, price_paise nullable, UPDATE price = price_paise / 100.0
```
