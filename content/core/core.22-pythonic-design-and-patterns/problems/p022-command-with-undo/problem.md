# Command pattern with undo and redo

An editor wants Undo and Redo. The **command pattern** turns every action into an **object**
that knows how to do itself and how to undo itself. A history keeps those objects on two
stacks.

`starter.py` has `Editor` (it just holds `text`), a half-written `Insert`, stubs, and a
`History` that cannot undo. Copy it to `solution.py` and build:

**Commands.** Each has `do()` and `undo()`. The constructor stores what it needs, **nothing
happens until `do()`**.

- `Insert(editor, pos, s)`: put `s` at index `pos` (`0 <= pos <= len(text)`).
- `Delete(editor, start, end)`: remove `text[start:end]` (`0 <= start <= end <= len(text)`).
  It must remember what it removed so `undo()` can put it back.
- `Replace(editor, start, end, new)`: replace `text[start:end]` with `new` (any length).
- `Macro(commands)`: a list of commands run as one. `do()` runs them in order, `undo()`
  undoes them in **reverse** order. Macros can contain macros.
- A command with a bad position raises `IndexError` **and leaves the text unchanged**. If a step
  inside a `Macro` fails, the macro undoes the steps it already did (in reverse) and re-raises,
  so a macro is all-or-nothing.

**`History`**

- `run(command)`: do it, remember it, and **clear the redo stack**. If `do()` raises, nothing is recorded.
- `undo()`: undo the latest command; return `True`, or `False` if there is nothing to undo.
- `redo()`: do the last undone command again; return `True`, or `False` if there is nothing to redo.

**Example**

```python
ed, h = Editor(), History()
h.run(Insert(ed, 0, "hello"))
h.run(Insert(ed, 5, " world"))     # 'hello world'
h.undo()                           # True, text is 'hello'
h.redo()                           # True, text is 'hello world'
h.undo()
h.run(Delete(ed, 0, 1))            # new command: redo history is gone
h.redo()                           # False
```
