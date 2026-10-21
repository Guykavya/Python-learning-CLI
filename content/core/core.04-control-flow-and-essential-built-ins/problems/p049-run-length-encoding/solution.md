## Approach

Keep the current character and how many times it has appeared in a row. When a different
character arrives, write out the finished run. After the loop, write out the last run.

## Code

```python
text = input()
if not text:
    print("(empty)")
else:
    result = ""
    current = text[0]
    count = 0
    for ch in text:
        if ch == current:
            count += 1
        else:
            result += f"{current}{count}"
            current = ch
            count = 1
    result += f"{current}{count}"
    print(result)
```

## Why the line after the loop

A run is only written when a **different** character comes after it. The last run has
nothing after it, so the loop never writes it. Forgetting this is the classic bug: `aaab`
would give `a3`.

## Why start with `current = text[0]` and `count = 0`

The loop then counts the first character itself, so every character is handled by the same
code. Starting with `count = 1` and looping over `text[1:]` also works.

## Another way

Compare each character with the next using `zip(text, text[1:] + "\0")`: write a run when they
differ. The extra end character forces the last run out.
