- Turning `log_and_double` into `[log(i) or i * 2 for i in items]`. It works, but a comprehension
  that exists for its side effect hides what the code does.
- `sum([1 for ...])` / `any([... for ...])`: the square brackets build a whole list first, and
  `any` cannot stop early. Remove the brackets.
- Making `first_duplicate` read the whole input (`seen`/`Counter` over everything) when the
  first repeat is enough.
- Writing a 3-clause comprehension for the triples. It is correct but hard to read, and still O(n^3).
- Reading a generator twice (for example `len(words)` and then a loop). A generator is empty the second time.
- Wrong order in `[x for row in matrix for x in row]`: the clauses read in the same order as the nested loops.
