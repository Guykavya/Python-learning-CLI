See the model answer shown when you check. The five tools are `in`, `partition`, `index`, `removesuffix` and `casefold`. A good answer gives, for each, the danger of the alternative:

1. `find` gives a position you do not need.
2. `split("=")` breaks values containing `=`.
3. `find` returns -1 silently, and -1 is a valid index.
4. `rstrip(".csv")` strips any of the characters `. c s v`, so `docs.csv` becomes `do`.
5. `lower()` does not match `ß` with `ss`.
