- `Delete` that does not save the removed text. `undo` then has nothing to put back.
- Recording the command before calling `do`. When `do` raises, the history contains a command that
  never happened.
- Forgetting to clear the redo stack on a new command. Redo would then apply an old change to a text
  it was never meant for.
- Undoing a macro in the same order as doing it. Later steps depend on earlier ones, so undo must go in
  reverse.
- A macro that stops at the failing step but does not roll back the earlier ones. The editor is left
  half-changed.
- Using `pop(0)` for the stacks. A stack takes from the end: `append` and `pop()`.
- Accepting any object with a `do` method in `execute`. Here the task asks for a real `Command`, so a
  fake without `undo` cannot get into the history.
