- **Leaving out rows 8 and 9, or keeping both.** The missing ids are one group; `first` keeps row 8, `last` keeps row 9.
- **Ordering the `last` result by key.** The result keeps the table's order: `[4, 5, 6, 7, 9]`, not `[6, 5, 4, 7, 9]`.
- **Thinking `keep=False` means "do not keep" in the sense of keeping nothing.** It keeps the rows that have **no**
  duplicate. Here: c and d.
- **Writing the first line as `first [1, 2, 4, 7]`.** The missing id counts: row 8 is the first of its group.
- **Mixing up the two counts on the last line.** The first counts the repeats, the second every member of a group.
- **Printing `'first'` with quotes.** `print(k, ...)` prints the text without quotes, and `False` as `False`.
