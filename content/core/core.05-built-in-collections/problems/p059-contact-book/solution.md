## Approach

Choose structures by the questions asked:

- "What is NAME's phone?" and "does NAME exist?": a dict `by_name`.
- "Who owns this phone?": a second dict `by_phone`. Searching `by_name.values()` would be O(n)
  per lookup.
- Sorted listings: sort only when printing, with `key=str.lower`. Python's stable sort keeps
  the insertion order of names that tie ignoring case, because `by_name` itself is in
  insertion order.

The main risk is letting the two dicts disagree. Every command that changes one changes the
other.

## Code

```python
by_name = {}
by_phone = {}
while True:
    parts = input().split()
    match parts:
        case ["quit"]:
            print("Goodbye")
            break
        case ["add", name, phone]:
            if name in by_name:
                print(f"{name} already exists")
            elif phone in by_phone:
                print(f"{phone} is already used by {by_phone[phone]}")
            else:
                by_name[name] = phone
                by_phone[phone] = name
                print(f"Added {name}")
        case ["update", name, phone]:
            if name not in by_name:
                print(f"No contact named {name}")
            elif phone in by_phone and by_phone[phone] != name:
                print(f"{phone} is already used by {by_phone[phone]}")
            else:
                del by_phone[by_name[name]]
                by_name[name] = phone
                by_phone[phone] = name
                print(f"Updated {name}")
        case ["delete", name]:
            if name in by_name:
                del by_phone[by_name.pop(name)]
                print(f"Deleted {name}")
            else:
                print(f"No contact named {name}")
        case ["phone", phone]:
            if phone in by_phone:
                print(f"{phone} belongs to {by_phone[phone]}")
            else:
                print(f"Unknown number {phone}")
        case ["find", prefix]:
            found = [n for n in sorted(by_name, key=str.lower) if n.lower().startswith(prefix.lower())]
            if not found:
                print("No matches")
            for n in found:
                print(f"{n}: {by_name[n]}")
        case ["list"]:
            if not by_name:
                print("Contact book is empty")
            for n in sorted(by_name, key=str.lower):
                print(f"{n}: {by_name[n]}")
        case ["count"]:
            print(f"Contacts: {len(by_name)}")
        case _:
            print("Unknown command")
```

## Complexity

`add`, `update`, `delete`, `phone` and `count` are O(1) on average. `find` and `list` are
O(n log n) because of sorting.

## Another way

Store only `by_name` and answer `phone` with a loop over `by_name.items()`. It is simpler and
correct, but each lookup is O(n), and 30,000 lookups over 30,000 contacts take far too long.
