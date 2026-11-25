## Hint 1

You already wrote every piece in the earlier problems and in the chapter: converters (`to_money`, `to_date`, `to_bool`, ...),
the flags of section 19.5 and the six questions of section 19.6. Which order do the steps have to run in? (Drop the duplicates on the **text**, convert, flag, write, then answer on the usable rows.) Write the plan as five comments before you write any code.

## Hint 2

```text
raw = read_csv(path, dtype="str");  removed = raw.duplicated().sum();  df = raw.drop_duplicates(ignore_index=True)
convert each column (title/lower text, money, percent, date, bool, Int64)
flag_date = not order_date.between(START, END)                       # NaT -> False -> flagged
flag_qty  = not qty.between(1, 50).fillna(False)                     # nullable: <NA> must be flagged
flag_price= not unit_price.between(10, 20000).fillna(False)
flag_id   = df.duplicated(subset=["order_id"], keep=False)
usable    = not any flag ; revenue = qty * unit_price * (1 - discount.fillna(0))
write clean.parquet, then problems.csv (six lines), then ok = df[usable] and the six answers
```
Test the pieces on the chapter's numbers: 1,205 rows after the duplicates, 1,142 usable, revenue 4,194,964.35.
