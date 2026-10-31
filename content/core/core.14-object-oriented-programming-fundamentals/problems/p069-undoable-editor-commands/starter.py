from abc import ABC, abstractmethod


class NothingToUndo(Exception):
    pass


class NothingToRedo(Exception):
    pass


class Command(ABC):
    # TODO: abstract do(editor), undo(editor), describe()
    pass


class Insert(Command):
    def __init__(self, pos, text):
        # TODO
        pass


class Delete(Command):
    def __init__(self, pos, length):
        # TODO
        pass


class Macro(Command):
    def __init__(self, name, commands):
        # TODO
        pass


class Editor:
    def __init__(self, text=""):
        self.text = text
        # TODO: undo and redo stacks
