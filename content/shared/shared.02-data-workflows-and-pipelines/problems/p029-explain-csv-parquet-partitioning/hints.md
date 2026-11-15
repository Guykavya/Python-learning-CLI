## Hint 1

For each scenario answer three questions before choosing: **who** reads the file (a person in a
spreadsheet, or code)? **How much** of it does a typical read need (all rows and columns, or a
few columns of the last few days)? **How big** is it in total and per partition? Then ask of any
proposed partition key: do the queries filter on it, and how many rows would each folder hold?

## Hint 2

```
format:      a person / Excel / no Python      -> CSV (document the columns, watch Excel's guesses)
             code, big, few columns per query   -> Parquet (columnar, compressed, typed)
partition:   key = the column most queries FILTER on (usually a date)
             granularity: each partition should hold many MB, not a handful of rows
             high-cardinality key (customer_id, hour for tiny data) -> small-files problem:
             folders x files x metadata cost more than the data itself
quick maths: rows per partition = total rows / number of partitions
```
