## Approach

The number of guesses is unknown, so use `while True:` and read one guess per pass.
The order of the checks matters:

1. Out of range first. Print `out of range` and `continue` **before** counting, so it does not count.
2. Count the guess.
3. Compare with the secret. On a match, print the message and `break`, so no further lines are read.

Because we stop reading at the correct guess, extra lines after it are never touched.

## Trace

First example (secret 42):

| pass | `guess` | in range? | `count` after | printed |
|---|---|---|---|---|
| 1 | 50 | yes | 1 | `lower` |
| 2 | 0 | no | 1 | `out of range` |
| 3 | 25 | yes | 2 | `higher` |
| 4 | 42 | yes | 3 | `correct in 3 guesses`, then `break` |

## Code

```python
secret = int(input())
count = 0
while True:
    guess = int(input())
    if guess < 1 or guess > 100:
        print("out of range")
        continue
    count += 1
    if guess < secret:
        print("higher")
    elif guess > secret:
        print("lower")
    else:
        print(f"correct in {count} guesses")
        break
```

## Complexity

One pass per input line up to the correct guess: O(g) for g guesses, with constant work per guess.

## Another way

Use a flag instead of `break`: `found = False` and `while not found:`, setting `found = True` on the match.
For the out-of-range case, wrap the counting and comparing in an `else:` instead of using `continue`.
This avoids `break` and `continue`, which some people find easier to read, but it adds a variable and nesting.
For a short loop like this, `break` and `continue` are clear and common.

## Edge cases

- Correct on the first guess: `correct in 1 guesses`.
- Guesses `0`, `101` and negatives: `out of range`, not `higher`/`lower`, and not counted.
- Secret 1 or 100: the boundaries are in range. `1` and `100` are valid guesses.
- Extra lines after the correct guess: never read.
