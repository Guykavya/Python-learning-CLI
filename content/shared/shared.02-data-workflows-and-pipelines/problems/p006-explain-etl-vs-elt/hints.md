## Hint 1

For each scenario ask three questions. Will the transformation rules change, and must old data
be re-done with the new rules? Can you read the source again later if you need to? Is the
destination allowed to see the raw data at all, and can it run transformations itself?

## Hint 2

```
rules change + old data must be redone + source forgets after 90 days -> keep raw -> ELT
destination must never see some fields + cannot transform anything  -> clean first -> ETL
for each: layers (raw/staging/clean or only the final file) + one row example
risk of ELT: raw layer is big and sensitive -> restrict access, retention
risk of ETL: a transform bug ships bad data, raw is not at the destination -> validate output, quarantine
```
