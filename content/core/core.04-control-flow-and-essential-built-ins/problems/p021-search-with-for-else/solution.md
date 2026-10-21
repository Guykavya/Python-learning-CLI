## Approach

A search: the loop looks at each word, `break`s on the first match, and the loop's `else`
reports failure, because it runs only when no `break` happened.

## Code

```python
target = input().strip()
sentence = input()
for n, word in enumerate(sentence.split(), start=1):
    if word.strip(".,!?").lower() == target.lower():
        print(f"Found '{target}' as word {n}")
        break
else:
    print(f"'{target}' not found")
```

## Why the `else` lines up with `for`

Indented under the `if`, it would print "not found" for every word that does not match.
Lined up with `for`, it runs once, after the loop, and only if nothing matched.

## Another way

A flag: `found = False` before the loop, `found = True` before `break`, and `if not found:` after.
