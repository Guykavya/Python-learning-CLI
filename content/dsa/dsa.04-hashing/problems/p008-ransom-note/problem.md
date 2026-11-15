# Ransom note

You want to write a note using letters cut out of a magazine. Each letter in the magazine can be used **at most once**.
Print `YES` if the note can be made from the magazine, otherwise `NO`.

## Input

- Line 1: the note (lower-case letters).
- Line 2: the magazine (lower-case letters).

## Output

`YES` or `NO`.

## Example

Input:

```
aab
baa
```

Output:

```
YES
```

The note needs two `a` and one `b`; the magazine has exactly that. With the magazine `ba` the answer is `NO`: there is
only one `a`. Using a set of letters would wrongly say `YES`.

## Constraints

- `1 <= len(note), len(magazine) <= 200000`
