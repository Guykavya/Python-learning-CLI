# An editor with undo and redo (the Command pattern)

Undo is easy if every change is an **object** that knows how to do itself and how to undo itself. The
editor keeps a stack of done commands; undo pops one and calls its `undo`. This is the **Command
pattern**.

In `solution.py` write:

### Exceptions

`NothingToUndo(Exception)` with the message `"nothing to undo"`, and `NothingToRedo(Exception)` with
`"nothing to redo"`. (Give each an `__init__` with no arguments that passes the message to
`super().__init__`.)

### `Command(ABC)`

Abstract methods `do(self, editor)`, `undo(self, editor)` and `describe(self)`.

### `Insert(Command)`

`Insert(pos, text)`.
- `do`: inserts `text` into `editor.text` at index `pos`. `pos` must be `0 <= pos <= len(editor.text)`,
  else `IndexError(f"insert position {pos} out of range")` and the text does not change.
- `undo`: removes exactly the inserted text again.
- `describe()`: `f"insert {self.text!r} at {self.pos}"`.

### `Delete(Command)`

`Delete(pos, length)`, `length >= 1`.
- `do`: removes `length` characters starting at `pos`. If `pos < 0` or `pos + length > len(editor.text)`,
  raise `IndexError(f"delete range {pos}..{pos + length} out of range")`. It remembers the removed
  text (in an attribute) for `undo`.
- `undo`: puts the removed text back at `pos`.
- `describe()`: `f"delete {self.length} at {self.pos}"`.

### `Macro(Command)`

`Macro(name, commands)`: several commands as one (composition: a command made of commands).
- `do`: runs the commands in order. If one raises, it first **undoes the ones that already ran** (in
  reverse order) and then re-raises the error, so the editor text is as before.
- `undo`: undoes all commands in **reverse** order.
- `describe()`: `f"macro {name} ({n} steps)"`.

### `Editor`

- `Editor(text="")`. Attribute `text`.
- `execute(command)`: if `command` is not a `Command`, raise
  `TypeError("execute() needs a Command")`. Calls `command.do(self)`. Only if that succeeds: push it on
  the undo stack and **clear** the redo stack.
- `undo()`: pops the last command, calls its `undo(self)`, pushes it on the redo stack. Empty undo stack:
  `NothingToUndo`.
- `redo()`: pops from the redo stack, calls `do(self)` again, pushes it on the undo stack. Empty:
  `NothingToRedo`.
- `can_undo()`, `can_redo()`: booleans.
- `history()`: a new list with `describe()` of every command on the undo stack, oldest first.

## Example

```python
ed = Editor("hello")
ed.execute(Insert(5, " world"))      # 'hello world'
ed.execute(Delete(0, 1))             # 'ello world'
ed.history()                         # ["insert ' world' at 5", 'delete 1 at 0']
ed.undo(); ed.text                   # 'hello world'
ed.redo(); ed.text                   # 'ello world'
ed.undo(); ed.undo(); ed.text        # 'hello'
ed.undo()                            # NothingToUndo: nothing to undo

ed.execute(Macro("greet", [Insert(0, "Oh, "), Delete(100, 1)]))   # IndexError: delete range 100..101 out of range
ed.text                              # 'hello'   (the first Insert was rolled back)
```
