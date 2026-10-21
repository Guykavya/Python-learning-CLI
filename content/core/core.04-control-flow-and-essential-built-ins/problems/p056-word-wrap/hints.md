## Hint 1

Keep the line you are building in a variable. For each word, ask: would the line still fit if
I added a space and this word?

## Hint 2

If the current line is empty, the word starts it (even if it is too long). If adding
`" " + word` keeps the length at most `W`, add it. Otherwise print the current line, count it,
and start a new line with the word.

## Hint 3

When the loop ends, the last line is still waiting in the variable. Print it if it is not
empty.
