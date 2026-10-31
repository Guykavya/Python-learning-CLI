## Hint 1

Start with `re.findall(r"#(\w+)", text)`. With one group, `findall` returns just the group: the name without `#`. Now try it on `"kavya@example.com"` with `@` instead of `#`. Why is that wrong, and what is the character just **before** the `@`?

## Hint 2

You need "the character before `#` is not a word character (or there is none)". `\b` is a boundary between a word and a non-word character; `\B` is the opposite. Since `#` itself is not a word character, `\B#` means "the character before `#` is not a word character either". Check it on `"a#b"`, `" #b"` and `"#b"`. (A lookbehind `(?<!\w)#` says the same thing.)

## Hint 3

```
hashtags = [h.lower() for h in findall(r"\B#(\w+)", text)]
mentions = findall(r"\B@(\w+)", text)

unique(items):          # keep the first of each, in order
    seen = set(); out = []
    for x in items:
        if x not in seen: add to seen, append to out
    return out

return {"hashtags": unique(hashtags), "mentions": unique(mentions)}
```
