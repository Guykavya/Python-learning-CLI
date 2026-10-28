## Hint 1

Run the first three lines of the problem example and print `a.tags is b.tags`. Two separate notes
give `True`. Where did that one shared list come from? Look at the `def __init__` line: when is the
default value `[]` created, once per call or once when Python runs the `def`?

## Hint 2

For the history: `self.history.append(...)` does not create anything; it **reads** `self.history`
and changes that list. If the object has no `history` of its own, which `history` does Python find
next (section 9 of the chapter)? How many such lists exist for all notes together?

## Hint 3

```
class Note:
    count = 0                         # keep: shared on purpose
    # remove the class-level history list

    def __init__(self, title, body="", tags=None):
        ...
        self.history = []             # one per note
        self.tags = []                # one per note, never the caller's list
        for tag in (tags or ()):
            clean it; if not empty and not already there: append
        Note.count += 1
```
