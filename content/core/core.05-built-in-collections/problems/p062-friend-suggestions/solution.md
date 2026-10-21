## Approach

A dict of sets is the standard way to store a network (a graph). Sets remove repeated
friendships and give O(1) "already a friend?" checks. Counting friends of friends with a dict
gives the number of mutual friends directly.

## Code

```python
friends = {}
for _ in range(int(input())):
    a, b = input().split()
    friends.setdefault(a, set()).add(b)
    friends.setdefault(b, set()).add(a)
for _ in range(int(input())):
    person = input().strip()
    mine = friends.get(person, set())
    counts = {}
    for f in mine:
        for g in friends[f]:
            if g != person and g not in mine:
                counts[g] = counts.get(g, 0) + 1
    top = sorted((-c, g) for g, c in counts.items())[:3]
    if top:
        print(f"{person}: " + ", ".join(f"{g} ({-c})" for c, g in top))
    else:
        print(f"{person}: no suggestions")
```

## Complexity

Building is O(n). For one query, the work is the sum of the friend counts of the person's
friends, plus sorting the candidates.
