## Hint 1

For each situation ask two questions: who or what reads the file next (a person, a script, a web service, a database), and what must survive (types, nesting, only a few columns)?

## Hint 2

```text
1 person + filters by hand      -> Excel
2 next script, types matter     -> Parquet (not CSV)
3 huge, few columns each time   -> Parquet (columnar)
4 nested lists inside records   -> JSON, flattened with json_normalize
5 data already in a database    -> query it (SQL with parameters)
```
