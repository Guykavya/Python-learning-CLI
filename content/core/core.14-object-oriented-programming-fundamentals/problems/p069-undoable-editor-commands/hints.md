## Hint 1

What does each command need to remember to undo itself? `Insert` knows its `pos` and `text`, so it can
cut them out again. `Delete` only knows `pos` and `length`: what must it save during `do`, so that `undo`
can put the text back?

## Hint 2

The editor has two lists used as stacks: `append` to push, `pop()` to take the last one. Draw them for
the example: after two `execute` calls, undo stack `[Insert, Delete]`, redo stack `[]`. After `undo`:
`[Insert]` and `[Delete]`. Why must a new `execute` clear the redo stack?

For `Macro.do`, keep a list of the commands that already succeeded. In `except`, undo them in reverse
order, then use a bare `raise`.

## Hint 3

```text
Delete.do(editor):
    end = pos + length
    if pos < 0 or end > len(editor.text): raise IndexError(...)
    self.removed = editor.text[pos:end]
    editor.text = editor.text[:pos] + editor.text[end:]

Macro.do(editor):
    done = []
    try:
        for c in commands: c.do(editor); done.append(c)
    except Exception:
        for c in reversed(done): c.undo(editor)
        raise

Editor.execute(c):
    if not isinstance(c, Command): raise TypeError(...)
    c.do(self)                 # if this raises, nothing below runs
    undo_stack.append(c); redo_stack.clear()
```
