## Hint 1

First call: compare 1 and 2 (take 1), 4 and 2 (take 2), 4 and 4 (tie, take left's 4), 7 and 4 (take right's 4), 7 and 9 (take 7). Then left is exhausted.

## Hint 2

After the loop the leftover `[9, 10]` of `right` is appended without a print. The function returns, and the outer `print` shows the full merged list.

## Hint 3

Second call: `left` is empty, so the `while` condition is false at once: no line is printed inside, only the returned list.
