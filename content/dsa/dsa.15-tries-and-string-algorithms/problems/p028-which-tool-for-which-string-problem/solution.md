## Approach

Match the **question** to the tool whose table answers it directly, after checking whether a built-in already does the job.

| Clue in the task | Label |
|---|---|
| plain search, once | `BUILTIN` |
| many prefix queries on a word list | `TRIE` |
| stream, borders, periods, repeated block | `KMP` |
| "how much of the beginning matches at each position" | `Z` |
| many equal-length patterns; equal substrings; longest repeat | `RK` |
| palindromes | `MANACHER` |

## Model answer

See `answer.md`.

## What to check

- You chose `BUILTIN` for task 2 instead of writing an algorithm.
- Your reasons name the **property** that decides (stream, equal lengths, starting vs ending at `i`, monotone length), not just the topic.
- Your two explanations count passes over the text or name the question the wrong tool answers.

## Another way

Test the choice with code on a small input: write the simplest correct version (often a built-in in a loop), time it on the given size, and switch tools only if it is too slow or cannot answer the question.
