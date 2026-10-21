## Walkthrough

| Code | Output | Why |
|---|---|---|
| `sorted(words)` | `['Banana', 'Fig', 'apple', 'date', 'kiwi', 'pear']` | uppercase first |
| `key=str.lower` | `['apple', 'Banana', 'date', 'Fig', 'kiwi', 'pear']` | case ignored |
| `key=len` | `['Fig', 'pear', 'kiwi', 'date', 'apple', 'Banana']` | ties keep input order |
| `key=len, reverse=True` | `['Banana', 'apple', 'pear', 'kiwi', 'date', 'Fig']` | longest first, ties still in input order |
| `key=len` then `[::-1]` | `['Banana', 'apple', 'date', 'kiwi', 'pear', 'Fig']` | reversing also flips the ties |
| `key=abs` | `[-1, 1, 2, 3, -3]` | -1 and 1 tie, as do 3 and -3; input order kept |
| `max`, `min` with `abs` | `3 -1` | first item with the largest / smallest key |
| `sorted(pairs)` | `[(1, 'y'), (1, 'z'), (2, 'a'), (2, 'b')]` | tuples compare item by item |
| `key=d.get` | `['y', 'x', 'z']` | sorted by value; `x` and `z` tie |
| with `reverse=True` | `['x', 'z', 'y']` | ties keep order |
| `nums.sort()` result | `None [-3, -1, 1, 2, 3]` | `sort` works in place |
