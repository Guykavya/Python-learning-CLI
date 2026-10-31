## Hint 1

Write the text that `writer` produces, row by row. Which cells get quotes: a cell with a comma, a cell with a
double quote, a cell with a newline, an empty cell, `None`?

## Hint 2

```
['id', 'note']     -> id,note
[1, 'plain']       -> 1,plain
[2, 'has, comma']  -> 2,"has, comma"
[3, 'say "hi"']    -> 3,"say ""hi"""      (a quote inside is doubled)
[4, 'two
lines']  -> 4,"two<newline>lines"   (this row uses two text lines)
[5, '']  and  [6, None]  -> both become an empty cell
```

Count `
` characters, then count lines, then count rows after reading back with `csv.reader`.
