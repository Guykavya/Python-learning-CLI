# Word Search II

`board` is a grid (a list of rows, each a list of one-letter strings) and `words` is a list of words. A word can be **traced** on the board if you can spell it by starting on some cell and stepping each time to a neighbouring cell (up, down, left or right), never using the same cell twice **within one word**.

Write `find_words(board, words)` that returns the **sorted** list of the distinct words that can be traced (chapter section 8). When the function returns, `board` must be exactly as it was.

## Example

```python
>>> board = [list("oaan"),
...          list("etae"),
...          list("ihkr"),
...          list("iflv")]
>>> find_words(board, ["oath", "pea", "eat", "rain"])
['eat', 'oath']
>>> find_words([list("ab")], ["ab", "ba", "aba"])     # 'aba' would reuse the cell 'a'
['ab', 'ba']
>>> find_words([list("a")], ["a", "a"])
['a']
```

## Constraints

- Boards up to 12 by 12; up to 3 * 10**4 words of 1 to 12 lowercase letters.
- One search per word is too slow on the tests: a 12 by 12 board of `a`s with a few other letters makes every unsuccessful word explore a huge number of paths. Search for **all words at once**, guided by a trie, within 10 seconds.

## Think about

1. When you stand on a cell during the DFS, which trie node are you at, and which neighbours are worth visiting?
2. How do you mark a cell as used, and what must happen when you leave it?
3. A word can be traced in several ways. How do you report it only once?
4. After a word is found, some trie branches lead to nothing any more. What can you do with them?
