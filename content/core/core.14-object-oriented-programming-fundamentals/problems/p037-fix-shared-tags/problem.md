# Fix: tags that leak between notes

Priya wrote a small notes class for her study app. Each note has a title, a body, a list of tags,
and an edit history so she can undo changes. It worked when she tried one note. With several notes,
strange things happen:

```python
a = Note("Lists")
a.add_tag("python")
b = Note("Shopping")
b.tags          # ['python']   <- b never got this tag!

a.edit("v2")
b.history       # ['']          <- b was never edited!

mine = ["exam"]
c = Note("OOP", tags=mine)
c.add_tag("revise")
mine            # ['exam', 'revise']   <- the caller's list changed
```

**This code has bugs. Find and fix them.** The starter is Priya's code. Copy it into
`solution.py` and fix it. There are **two** bugs, both about objects sharing one list when each
should have its own. (The third symptom above comes from the same bug as the first.)

What the class must do (Priya's code already tries to do all of this):

- `Note(title, body="", tags=...)`: `tags` is optional; when given, it is any iterable of strings.
  Every note has its **own** `tags` list. Tags are cleaned with `strip().lower()`, duplicates are
  dropped, first order is kept. The caller's list must never be changed by the note.
- `add_tag(tag)`: cleans the tag; an empty tag raises `ValueError`; a tag already there is ignored.
- `remove_tag(tag)`: cleans the tag and removes it; a missing tag raises `KeyError`.
- `edit(new_body)`: saves the old body in the note's own `history` list, then sets `body`.
- `undo_edit()`: puts back the last saved body; with nothing to undo, raises
  `IndexError("nothing to undo")`.
- `Note.count` is a class attribute counting how many notes were created. This one **should** be
  shared, and it already works: do not break it.

**Example** (after the fix)

```python
a = Note("Lists", tags=[" Python ", "python", "Basics"])
a.tags              # ['python', 'basics']
b = Note("Shopping")
b.tags              # []
a.edit("v2"); a.edit("v3")
a.undo_edit()
a.body, a.history   # ('v2', [''])
b.history           # []
```
