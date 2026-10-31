## Approach

The writer produces this text:

```text
id,note
1,plain
2,"has, comma"
3,"say ""hi"""
4,"two
lines"
5,
6,
```

- There are 8 newline characters: 7 rows, plus one newline inside the cell of row 4. That is why the count is
  8 and `splitlines()` also gives 8 lines.
- `lines[3]` is row 3. A double quote inside a cell is written twice, and the whole cell is quoted.
- `lines[4]` and `lines[5]` are the two halves of row 4. The cell is split over two text lines.
- `csv.reader` joins them again: 7 rows, and row 4 has the cell `'two\nlines'`.
- `""` and `None` both become an empty cell, so reading back gives `''` for both (the `None` is lost).
- `rows[1][0] + rows[2][0]` is `'1' + '2'`, because every cell is read back as text.

## Output

```text
8
8
3,"say ""hi"""
4,"two
lines"
7
['3', 'say "hi"']
['4', 'two\nlines']
['5', ''] ['6', '']
12
```

## Complexity

Not applicable.

## Another way

Print `repr(text)` once. You will see the whole text with every `\n` and quote, which is the easiest way to
check this kind of problem.
