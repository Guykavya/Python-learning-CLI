class Editor:
    def __init__(self, text=""):
        self.text = text


class Insert:
    def __init__(self, editor, pos, s):
        self.editor, self.pos, self.s = editor, pos, s

    def do(self):
        t = self.editor.text
        self.editor.text = t[: self.pos] + self.s + t[self.pos:]

    def undo(self):
        raise NotImplementedError


class Delete:
    def __init__(self, editor, start, end):
        raise NotImplementedError


class Replace:
    def __init__(self, editor, start, end, new):
        raise NotImplementedError


class Macro:
    def __init__(self, commands):
        raise NotImplementedError


class History:
    def __init__(self):
        self.done = []

    def run(self, command):
        command.do()
        self.done.append(command)

    def undo(self):
        raise NotImplementedError

    def redo(self):
        raise NotImplementedError
