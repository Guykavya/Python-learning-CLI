# Word pattern

You get a **pattern** of letters and a sentence of words. The sentence **follows the pattern** if there is a
one-to-one match between pattern letters and words: the same letter always stands for the same word, and different
letters stand for different words. Print `YES` or `NO`.

## Input

- Line 1: the pattern (lower-case letters, no spaces).
- Line 2: the words, separated by single spaces.

## Output

`YES` or `NO`.

## Example

Input:

```
abba
dog cat cat dog
```

Output:

```
YES
```

`a = dog`, `b = cat`. For `dog cat cat fish` the answer is `NO` (the second `a` would be `fish`). For
`dog dog dog dog` it is `NO` (`a` and `b` would both be `dog`). If the pattern and the sentence have different lengths,
the answer is `NO`.

## Constraints

- `1 <= len(pattern) <= 100000`, and the sentence has at most `100000` words.
