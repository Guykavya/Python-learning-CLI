# Isomorphic strings

Two strings `s` and `t` of the same length are **isomorphic** if you can replace the characters of `s` to get `t`
with a consistent rule: the same character always becomes the same replacement, and two different characters never
become the same replacement. (A character may map to itself.)

Print `YES` if they are isomorphic, otherwise `NO`.

## Input

- Line 1: `s`.
- Line 2: `t` (the same length).

## Output

`YES` or `NO`.

## Example

Input:

```
egg
add
```

Output:

```
YES
```

`e -> a`, `g -> d`. For `foo` and `bar`, `o` would have to become both `a` and `r`: `NO`.
For `ab` and `aa`, `a -> a` and `b -> a` sends two different characters to one: `NO`.

## Constraints

- `1 <= len(s) = len(t) <= 200000`
