## Approach

- `available` and `total`: dicts from title to counts.
- `loans`: dict from member to a set of titles. A set fits because a member holds each title at
  most once and order does not matter (we sort when printing).

## Code

```python
available = {}
total = {}
loans = {}
while True:
    parts = input().split()
    match parts:
        case ["close"]:
            break
        case ["addbook", title, n]:
            available[title] = available.get(title, 0) + int(n)
            total[title] = total.get(title, 0) + int(n)
            print(f"{title}: {available[title]} copies available")
        case ["borrow", member, title]:
            held = loans.setdefault(member, set())
            if title not in total:
                print(f"No such book {title}")
            elif title in held:
                print(f"{member} already has {title}")
            elif len(held) >= 3:
                print(f"{member} has reached the limit")
            elif available[title] == 0:
                print(f"{title} is not available")
            else:
                held.add(title)
                available[title] -= 1
                print(f"{member} borrowed {title}")
        case ["return", member, title]:
            held = loans.get(member, set())
            if title in held:
                held.remove(title)
                available[title] += 1
                print(f"{member} returned {title}")
            else:
                print(f"{member} does not have {title}")
        case ["member", member]:
            held = loans.get(member, set())
            if held:
                print(f"{member} has: {', '.join(sorted(held))}")
            else:
                print(f"{member} has nothing")
for title in sorted(total):
    print(f"{title}: {available[title]}/{total[title]}")
```

## Complexity

Every command is O(1) on average, except `member` (sorts at most 3 titles) and the final report
(sorts the titles).
