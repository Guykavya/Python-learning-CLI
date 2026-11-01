## Hint 1

Read the function line by line and ask for each line: *what job is this (file, parsing,
pricing, logging, printing)?* A function with many jobs has many reasons to change. Also ask:
what does the caller lose or get by surprise (changed rows, a global list, printed text)?

## Hint 2

Use this four-part outline:

```
1. Problems:   names / flag argument / mixed levels / side effects / resource leak / bare except / loop style / noisy comments
2. Names:      one new name per thing
3. Split:      load_rate(path)  ->  row_total(row, rate)  ->  price_rows(rows, rate)  ->  main prints
4. First test: a characterization test of the CURRENT behavior, before any edit
```

For part 4 think about *why first*: what can you not know after the change if you did not
record the behavior before it?
