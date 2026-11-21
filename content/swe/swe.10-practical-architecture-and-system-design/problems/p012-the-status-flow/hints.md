## Hint 1

Write the four allowed moves as data first. What is the natural key of a move, and what is the value? Then the function has three steps: check the words are known, look the move up, and decide what to raise when the lookup fails.

## Hint 2

```text
TRANSITIONS = {("todo", "start"): "doing", ("doing", "pause"): "todo", ("doing", "finish"): "done", ("done", "reopen"): "todo"}
unknown status or action -> ValueError
(current, action) in the table -> its value
otherwise RuleViolation(f"cannot {action} a task that is {current}")
```
