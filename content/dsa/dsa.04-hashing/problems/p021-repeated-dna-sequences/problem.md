# Repeated DNA segments

A DNA string `s` uses the letters `A`, `C`, `G`, `T`. Given a length `L`, find every **distinct** substring of length
`L` that occurs **at least twice** in `s` (the occurrences may overlap).

Keep two sets while sliding a window of size `L` across `s`: the segments seen once, and the segments already
reported as repeated.

## Input

- Line 1: `s`.
- Line 2: `L`.

## Output

- Line 1: the number `c` of repeated segments.
- Line 2: the segments in alphabetical order, separated by spaces (an empty line when `c = 0`).

## Example

Input:

```
AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT
10
```

Output:

```
2
AAAAACCCCC CCCCCAAAAA
```

Both segments appear twice. For `AAAA` and `L = 2` the segment `AA` occurs three times (overlapping) and is reported once.

## Constraints

- `1 <= L <= len(s) <= 200000`, and `L <= 20` in the tests.
