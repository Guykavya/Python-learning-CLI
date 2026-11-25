## Approach

Line by line: the header splits into 3 fields; the quoted comma stays inside `'Pune, MH'` (3 fields); `""` becomes one `"` in `'say "hi"'` (3 fields); `'Chen '` and `' 70'` keep their spaces (3 fields); the empty line gives `[]` (0 fields, and it still consumes a line number); `Dev,Goa` has only 2 fields. The exact printed text is in `expected.txt`, taken from a real run.

## Code

See the program in the problem statement.

## Complexity

O(total characters).

## Another way

`csv.DictReader` skips completely empty lines and fills missing fields of a short row with `None` (`restval`), which is convenient but hides the problem; counting `len(row)` yourself shows it.
