## Hint 1

What does `id(a) == id(b)` tell you? How is that related to `a is b`?

## Hint 2

Search the chapter for the range of integers that CPython keeps ready-made. Is this promised by the
language, or by one implementation?

## Hint 3

Think of a value computed at run time, like `int(input())` when the user types 7. Would it be the
cached object? Would `int("1000") is int("1000")` be safe to rely on?
