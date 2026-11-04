# First character that appears once

Given a string `s` of lower-case letters, print the **0-based index** of the first character that occurs **exactly
once** in the whole string. Print `-1` if there is no such character.

Two passes work: first count every character, then scan the string again and stop at the first one whose count is 1.

## Input

One line: the string `s`.

## Output

One integer.

## Example

Input:

```
loveleetcode
```

Output:

```
2
```

`l` appears 2 times, `o` 2 times, `v` once. The first character with count 1 is `v` at index 2.
For `aabb` the answer is `-1`.

## Constraints

- `1 <= len(s) <= 200000`
- `s` has only the letters `a` to `z`.
