## Hint 1

Read each snippet and ask: "what surprises the next person?" For 1, call the function twice in
your head. For 2, what could go wrong *besides* a bad number? For 6, what does the caller write
after the call?

## Hint 2

Use this shape for every snippet: **Smell** (a name), **Hurts** (one concrete failure), **Fix** (code).

```
1 default created once      -> None default
2 catches too much          -> except ValueError
3 type(x) == list           -> isinstance / accept any iterable
4 += in a loop              -> "".join(...)
5 `l`, loop = filter        -> descriptive name, comprehension
6 False or a User           -> None / raise / default
```
