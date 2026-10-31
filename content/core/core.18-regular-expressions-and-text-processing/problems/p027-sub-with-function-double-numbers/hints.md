## Hint 1

Start with `re.sub(r"\d+", f, s)` where `f(m)` returns `str(int(m.group()) * 2)`. Run it on
`"mp3"` and `"2.5"`. Which unwanted matches do you get? What must be true just **before** and just
**after** a real integer?

## Hint 2

Use a lookbehind for "the character before is not a word character and not a dot":
`(?<![\w.])`, and a lookahead for "after it comes no word character and no `.digit`":
`(?!\w|\.\d)`. Is `-` a word character? So what happens to `-4`: is the `4` found, and what
does the text look like after it is doubled?

## Hint 3

```
INT = (?<![\w.])\d+(?!\w|\.\d)

def double(m):
    return str(int(m.group()) * 2)

return re.sub(INT, double, s)
```
