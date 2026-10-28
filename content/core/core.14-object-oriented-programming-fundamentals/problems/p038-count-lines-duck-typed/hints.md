## Hint 1

What do a list, a file, an `io.StringIO` and a generator have in common? You can write
`for line in source:` for all of them. If your function does only that, does it need to know which
one it got? Why is a `str` the dangerous exception?

## Hint 2

`first_line` can `return` from inside the `for` loop the moment it finds a line. The loop stops
there and nothing more is read. For `Lines`, a method `__iter__` that contains `yield` is a
generator function: every `for` calls it again and gets a brand-new generator that starts at the
first line.

## Hint 3

```
count_nonblank(source, comment=None):
    if isinstance(source, str): raise TypeError("pass lines, not one string")
    count = 0
    for line in source:
        text = line.strip()
        if text == "": skip
        if comment is not None and text.startswith(comment): skip
        count += 1
    return count

class Lines:
    __iter__(self):
        for line in self.text.splitlines(): yield line
```
