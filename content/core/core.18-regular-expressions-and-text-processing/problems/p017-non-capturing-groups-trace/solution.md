## Approach

Count the capturing groups first, then apply the findall rule, then the "last repetition"
rule for repeated groups.

## Line by line

1. `(ab)+` has one group, so findall returns group 1 of each match. The three matches are
   `ababab`, `ab` (in `abx`) and `ab`, but group 1 keeps only the last repetition: `'ab'` each time.
2. `(?:ab)+` has no capturing group: whole matches, `['ababab', 'ab', 'ab']`.
3. In `"xababab"` the match starts at 1 and ends at 7. Group 1 is the last `ab`, at (5, 7).
4. `(a)(b)` has two groups: tuples `('a', 'b')`.
5. `(?:a)(b)` has one capturing group: just `'b'`.
6. `(red|green) apple` captures the colour only: `['red', 'green']`.
7. `(?:red|green) apple`: no capture, whole matches `['red apple', 'green apple']`.
8. `red|green apple` without brackets: the alternatives are `red` and `green apple`, so the
   first match is just `red`.
9. `(?:ab)+(c)?` on `"ababd"`: the `(c)?` group does not take part, so it is `None`. There is
   still one group, so `groups()` is `(None,)` and its length is 1.
10. `re.split(r"(-)", ...)` keeps the captured separators.
11. `re.split(r"(?:-)", ...)` does not: same as splitting on `-`.

## Expected output

```
['ab', 'ab', 'ab']
['ababab', 'ab', 'ab']
ababab ab (1, 7) (5, 7)
[('a', 'b'), ('a', 'b')]
['b', 'b']
['red', 'green']
['red apple', 'green apple']
['red', 'green apple']
abab (None,) 1
['a', '-', 'b', '-', 'c']
['a', 'b', 'c']
```

## Complexity

Every call is linear in the length of the text here.

## Another way

When you need the whole match **and** the groups, use `re.finditer` instead of `findall`:
each item is a Match object, so `m.group(0)` and `m.group(1)` are both available and nothing
depends on how many groups the pattern has.
