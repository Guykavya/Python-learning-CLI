## Approach

- **Command objects** (polymorphism, chapter section 15): the editor calls `do`, `undo` and `describe`
  without knowing which command it has. `Command(ABC)` (chapter section 16) makes sure every command
  implements all three.
- **Two stacks:** done commands go on the undo stack; undone ones on the redo stack. A new command
  starts a new "future", so the redo stack is cleared.
- **Fail without changes:** each command checks its range **before** changing the text, and `execute`
  records a command only after `do` returned. An exception skips the recording automatically.
- **Composite** (composition, chapter section 14): `Macro` is a `Command` that *has* commands. It gives
  "all or nothing" by undoing the finished steps when a later one fails, the same idea as the bank
  transfer rollback in p063.

## Code

```python
from abc import ABC, abstractmethod


class NothingToUndo(Exception):
    def __init__(self):
        super().__init__("nothing to undo")


class NothingToRedo(Exception):
    def __init__(self):
        super().__init__("nothing to redo")


class Command(ABC):
    @abstractmethod
    def do(self, editor):
        ...

    @abstractmethod
    def undo(self, editor):
        ...

    @abstractmethod
    def describe(self):
        ...


class Insert(Command):
    def __init__(self, pos, text):
        self.pos = pos
        self.text = text

    def do(self, editor):
        if not 0 <= self.pos <= len(editor.text):
            raise IndexError(f"insert position {self.pos} out of range")
        editor.text = editor.text[:self.pos] + self.text + editor.text[self.pos:]

    def undo(self, editor):
        end = self.pos + len(self.text)
        editor.text = editor.text[:self.pos] + editor.text[end:]

    def describe(self):
        return f"insert {self.text!r} at {self.pos}"


class Delete(Command):
    def __init__(self, pos, length):
        self.pos = pos
        self.length = length
        self.removed = ""

    def do(self, editor):
        end = self.pos + self.length
        if self.pos < 0 or end > len(editor.text):
            raise IndexError(f"delete range {self.pos}..{end} out of range")
        self.removed = editor.text[self.pos:end]
        editor.text = editor.text[:self.pos] + editor.text[end:]

    def undo(self, editor):
        editor.text = editor.text[:self.pos] + self.removed + editor.text[self.pos:]

    def describe(self):
        return f"delete {self.length} at {self.pos}"


class Macro(Command):
    def __init__(self, name, commands):
        self.name = name
        self.commands = list(commands)

    def do(self, editor):
        done = []
        try:
            for command in self.commands:
                command.do(editor)
                done.append(command)
        except Exception:
            for command in reversed(done):
                command.undo(editor)
            raise

    def undo(self, editor):
        for command in reversed(self.commands):
            command.undo(editor)

    def describe(self):
        return f"macro {self.name} ({len(self.commands)} steps)"


class Editor:
    def __init__(self, text=""):
        self.text = text
        self._undo = []
        self._redo = []

    def execute(self, command):
        if not isinstance(command, Command):
            raise TypeError("execute() needs a Command")
        command.do(self)
        self._undo.append(command)
        self._redo.clear()

    def undo(self):
        if not self._undo:
            raise NothingToUndo()
        command = self._undo.pop()
        command.undo(self)
        self._redo.append(command)

    def redo(self):
        if not self._redo:
            raise NothingToRedo()
        command = self._redo.pop()
        command.do(self)
        self._undo.append(command)

    def can_undo(self):
        return bool(self._undo)

    def can_redo(self):
        return bool(self._redo)

    def history(self):
        return [command.describe() for command in self._undo]
```

## Complexity

Each command is O(n) for a text of length n, because strings are immutable and slicing copies them.
The stacks make `undo`/`redo` themselves O(1) plus the command's work.

## Another way

Store a full copy of the text before each change ("memento") and undo by restoring it. That needs no
`undo` logic per command, but it uses memory proportional to text size times history length. Real
editors use commands like these, often merging many small inserts (typing) into one command.
