# Sort students by score then name

Each student has a name and an integer score. Print the students ordered by **score from highest to lowest**; students with the same score are
ordered by **name alphabetically** (A to Z). Practise the *key tuple* with a negated number.

## Input

- Line 1: `n`.
- Next `n` lines: `name score` (the name is one word of lowercase letters).

## Output

`n` lines `name score` in the required order.

## Constraints

- `1 <= n <= 100000`
- `0 <= score <= 10^9`

## Example

Input:

```
5
zoe 90
ann 85
bob 90
cy 70
dee 85
```

Output:

```
bob 90
zoe 90
ann 85
dee 85
cy 70
```
