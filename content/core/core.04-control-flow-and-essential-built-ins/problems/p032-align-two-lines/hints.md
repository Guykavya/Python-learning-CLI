## Hint 1

You need each column's width before you print the first line. Can you work out the width of
a column from just the two words in it?

## Hint 2

Walk both lines together with `zip`. For each pair, `width = max(len(top), len(bottom))`. Build
both output lines in the same loop.

## Hint 3

Format with a variable width: `f"{word:>{width}}"` or `f"{word:<{width}}"`. Choose the
alignment for each word separately with a conditional expression. Strip the end of each line.
