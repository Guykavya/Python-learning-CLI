## Approach

Both bugs are the same mistake in two forms: **one list object is shared** where every note needs
its own. `a.tags is b.tags` and `a.history is b.history` print `True` in the starter. That is the
quickest way to see it.

**Bug 1: the mutable default argument.** `def __init__(self, title, body="", tags=[])` creates the
list `[]` **once**, when Python runs the `def` line. Every `Note(...)` made without `tags` gets that
same list, and `self.tags = tags` stores it. So `a.add_tag("python")` puts the tag into the one
default list, and `b` sees it. When the caller passes a list, `self.tags = tags` stores the
**caller's** list, and `self.tags[:] = cleaned` and `add_tag` then change it (aliasing).
Fix: `tags=None`, and always build a fresh list `self.tags = []` and append the cleaned tags.

**Bug 2: the mutable class attribute.** `history = []` in the class body is a class attribute: one
list for the whole class. `self.history.append(...)` does not assign anything. It looks up
`history`, finds nothing on the object, finds the class's list (chapter section 5 and section 9),
and changes it. Fix: create `self.history = []` in `__init__` and remove the class attribute.

**Why `count` is fine.** `Note.count += 1` assigns a new number to the **class** attribute. That is
exactly what a shared counter should do. (`self.count += 1` would have been a bug: it would create
an instance attribute on each note and leave `Note.count` at 0.)

## Code

```python
class Note:
    count = 0                       # shared on purpose: one counter for the whole class

    def __init__(self, title, body="", tags=None):
        self.title = title
        self.body = body
        self.history = []           # bug 2 fixed: each note gets its own history list
        self.tags = []              # bug 1 fixed: a new list per note, never the caller's list
        for tag in tags or ():
            tag = tag.strip().lower()
            if tag and tag not in self.tags:
                self.tags.append(tag)
        Note.count += 1

    def add_tag(self, tag):
        tag = tag.strip().lower()
        if not tag:
            raise ValueError("a tag cannot be empty")
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        tag = tag.strip().lower()
        if tag not in self.tags:
            raise KeyError(tag)
        self.tags.remove(tag)

    def edit(self, new_body):
        self.history.append(self.body)
        self.body = new_body

    def undo_edit(self):
        if not self.history:
            raise IndexError("nothing to undo")
        self.body = self.history.pop()
```

`tags or ()` turns `None` into an empty tuple, so the loop simply does nothing.

## Complexity

Building the tags is O(k²) for k tags because of `tag not in self.tags` on a list; for a handful of
tags that does not matter. Everything else is O(1) (`remove_tag` is O(k)).

## Another way

`tags=()` as the default also works: a tuple cannot be changed, so sharing it is harmless. What
matters is that the note never stores the default (or the caller's object) itself; it builds its
own list. You can see the shared default directly: `Note.__init__.__defaults__` shows the default
values, and in the starter the `[]` there fills up with tags.
