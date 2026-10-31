## Hint 1

For each `findall` line, first count the capturing groups in the pattern. `(?:` does not count.
Zero groups: the list holds whole matches. One group: it holds only what that group caught.
Two or more: tuples.

## Hint 2

For `(ab)+` on `"ababab"` the whole match is `ababab`, but group 1 was overwritten on every
repetition. Which `ab` is the last one, and at which index does it start? `m.span()` is the whole
match, `m.span(1)` is only group 1.

## Hint 3

`|` has the **lowest** priority of all. `red|green apple` means "`red`" OR "`green apple`", not
"`red apple`" or "`green apple`". Walk the string left to right and note what each alternative
can take.
