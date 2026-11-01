## Approach

- **Command**: an action as an object with `do()` and `undo()`. Information needed to undo is
  captured while doing (`removed`, `old`).
- **Composite**: `Macro` is a command made of commands, so `History` treats one action and a
  bundle the same way.
- **Two stacks**: `undo` moves a command from the undo stack to the redo stack; `redo` moves it
  back; `run` pushes on the undo stack and empties the redo stack, because a new action
  rewrites the future.
- **Atomic macro**: undo the finished steps in reverse if a later one fails.
- Validate **before** changing anything, so a failing command leaves no half-change.

## Code

```python
class Editor:
    def __init__(self, text=""):
        self.text = text


class Insert:
    def __init__(self, editor, pos, s):
        self.editor, self.pos, self.s = editor, pos, s

    def do(self):
        t = self.editor.text
        if not 0 <= self.pos <= len(t):
            raise IndexError(f"cannot insert at {self.pos} in text of length {len(t)}")
        self.editor.text = t[: self.pos] + self.s + t[self.pos:]

    def undo(self):
        t = self.editor.text
        self.editor.text = t[: self.pos] + t[self.pos + len(self.s):]


class Delete:
    def __init__(self, editor, start, end):
        self.editor, self.start, self.end = editor, start, end
        self.removed = ""

    def do(self):
        t = self.editor.text
        if not 0 <= self.start <= self.end <= len(t):
            raise IndexError(f"bad range {self.start}:{self.end} for length {len(t)}")
        self.removed = t[self.start:self.end]
        self.editor.text = t[: self.start] + t[self.end:]

    def undo(self):
        t = self.editor.text
        self.editor.text = t[: self.start] + self.removed + t[self.start:]


class Replace:
    def __init__(self, editor, start, end, new):
        self.editor, self.start, self.end, self.new = editor, start, end, new
        self.old = ""

    def do(self):
        t = self.editor.text
        if not 0 <= self.start <= self.end <= len(t):
            raise IndexError(f"bad range {self.start}:{self.end} for length {len(t)}")
        self.old = t[self.start:self.end]
        self.editor.text = t[: self.start] + self.new + t[self.end:]

    def undo(self):
        t = self.editor.text
        self.editor.text = t[: self.start] + self.old + t[self.start + len(self.new):]


class Macro:
    def __init__(self, commands):
        self.commands = list(commands)

    def do(self):
        done = []
        try:
            for command in self.commands:
                command.do()
                done.append(command)
        except Exception:
            for command in reversed(done):
                command.undo()
            raise

    def undo(self):
        for command in reversed(self.commands):
            command.undo()


class History:
    def __init__(self):
        self._undo = []
        self._redo = []

    def run(self, command):
        command.do()
        self._undo.append(command)
        self._redo.clear()

    def undo(self):
        if not self._undo:
            return False
        command = self._undo.pop()
        command.undo()
        self._redo.append(command)
        return True

    def redo(self):
        if not self._redo:
            return False
        command = self._redo.pop()
        command.do()
        self._undo.append(command)
        return True
```

## Complexity

Each command is O(len(text)) because strings are rebuilt. `History` operations are O(1) plus the command's cost; a macro is the sum of its steps.

## Another way

All three text commands are one operation: *replace `text[start:end]` with `new`*
(`Insert` is `start == end`, `Delete` is `new == ""`). One `_Splice` class plus three tiny
factory functions removes the repeated code. Other designs store **snapshots** (the whole text
before each command): trivial to undo but memory-hungry. Commands store only the difference.
