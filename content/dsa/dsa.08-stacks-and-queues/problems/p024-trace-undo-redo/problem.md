# Trace: undo and redo

This is the chapter's `Editor` (section 8, "Undo and redo"): two stacks, one of earlier texts (`undo_stack`) and one of undone texts (`redo_stack`). A script of 14 commands runs on it, and after each command the program prints the command, the text, and the **sizes** of the two stacks.

Predict **exactly** what it prints. Do not run it.

```python
class Editor:
    def __init__(self):
        self.text = ""
        self.undo_stack = []
        self.redo_stack = []

    def type(self, s):
        self.undo_stack.append(self.text)
        self.text += s
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.text)
            self.text = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.text)
            self.text = self.redo_stack.pop()


e = Editor()
script = ["type hi", "type _there", "undo", "type !", "undo", "undo",
          "redo", "redo", "redo", "type ?", "redo", "undo", "undo", "undo"]
for command in script:
    if command.startswith("type "):
        e.type(command[5:])
    elif command == "undo":
        e.undo()
    else:
        e.redo()
    print(command, repr(e.text), len(e.undo_stack), len(e.redo_stack))
```

Write your answer in `answer.txt`, one printed line per line, for example `type hi 'hi' 1 0` (the command, the text in quotes as `repr` shows it, the size of `undo_stack`, the size of `redo_stack`).

## How to work

Draw three boxes: `text`, `undo_stack` (a list, top on the right) and `redo_stack`. For every command, update all three. Remember the three rules:

- `type` saves the current text on `undo_stack`, adds to the text, and **clears** `redo_stack`;
- `undo` (only if `undo_stack` is not empty) saves the current text on `redo_stack` and takes the text back from `undo_stack`;
- `redo` (only if `redo_stack` is not empty) does the opposite.

## After you answer

1. Why does the third `redo` print the same line as the second?
2. Why does `redo` after `type ?` do nothing, although you undid several things before?
3. After the last line, how many more `redo` commands would change the text, and what would the texts be?
