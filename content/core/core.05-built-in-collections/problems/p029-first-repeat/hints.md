## Hint 1

Walk the words once, left to right. The first time you meet a word you have already seen,
you are done. Why?

## Hint 2

Keep `first_pos = {}`. For each `(i, word)`: if `word in first_pos`, print and stop; otherwise
store `first_pos[word] = i`.

## Hint 3

Use `enumerate(words, start=1)` for positions. Use a flag or `for`-`else` to print `No repeats`.
