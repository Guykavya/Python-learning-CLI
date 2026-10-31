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
