## Hint 1

Try removing one element. If the program still fails without it, was that element needed? What do you do next: keep the smaller list or put the element back?

## Hint 2

After a successful removal, the same index now holds the next element, so do **not** advance the index. After a full pass without any removal, you are finished; after a pass with removals, go again (an element that was needed before may be unneeded now).

## Hint 3

```text
if not fails(case): raise ValueError
case = list(case)
changed = True
while changed:
    changed = False
    i = 0
    while i < len(case):
        candidate = case without position i
        if fails(candidate): case = candidate; changed = True    # stay at i
        else: i += 1
return case
```
