## Hint 1

A `Flag` member is a bit. How do you ask "is this bit set in that combination"? (The `in` operator.) How do you make the empty combination? (`Permission(0)`.) For `parse`, what does each of the three positions have to contain?

## Hint 2

`describe`: for each pair `(letter, flag)` use `letter if flag in perm else "-"` and join. `parse`: start with `Permission(0)`; for each position, the character must be the expected letter (then `result |= flag`) or `-` (nothing) or else raise `ValueError`. `allows`: `needed in granted` already means "all bits of needed are in granted" for flags. `highest`: `max(iterable, default=None)`.

## Hint 3

```
describe: "".join(letter if flag in perm else "-" for letter, flag in (("r", READ), ("w", WRITE), ("x", EXECUTE)))
parse: len must be 3 ; result = Permission(0)
       for char, expected, flag in zip(text, "rwx", flags): char == expected -> result |= flag ; char == "-" -> skip ; else ValueError
allows: return needed in granted
highest: return max(priorities, default=None)
```
