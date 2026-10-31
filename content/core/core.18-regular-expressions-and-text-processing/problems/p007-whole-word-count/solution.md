## Approach

1. `re.escape(word)` turns `node.js` into `node\.js` and `c+d` into `c\+d`, so special
   characters are matched literally.
2. Wrap it in `\b ... \b` so only whole words count. `\b` uses up no characters, it only checks
   that a word character meets a non-word character (or the string edge) at that spot.
3. `re.IGNORECASE` makes the comparison ignore case.
4. `len(re.findall(...))` counts the matches.

## Code

```python
import re


def count_word(text: str, word: str) -> int:
    pattern = r"\b" + re.escape(word) + r"\b"
    return len(re.findall(pattern, text, re.IGNORECASE))
```

Why the task promises that `word` starts and ends with a letter or digit: `\b` needs a word
character on one side. For a word like `c++`, the `\b` after the last `+` would need a word
character **after** it, which is the opposite of what you want. Such words need lookarounds
like `(?<!\w)` and `(?!\w)` (later in this chapter).

## Complexity

O(n) for a text of length n.

## Another way

`sum(1 for _ in re.finditer(pattern, text, re.I))` counts without building the list.
Without regex you could split the text into words with your own rules, but deciding where words
end (punctuation, hyphens, quotes) is exactly what `\b` already does for you.
