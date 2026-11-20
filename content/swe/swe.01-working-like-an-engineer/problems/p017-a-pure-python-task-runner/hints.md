## Hint 1

Describe each task as **data**: a list of commands. Which structure maps a task name to its commands? How is `check` built from the others?

## Hint 2

Loop over the commands of the chosen task. After each `run(cmd)`, look at the exit code: when is it right to go on, and when to return at once?

## Hint 3

```text
TASKS = {"test": [...], "lint": [...], "types": [...]}
TASKS["check"] = lint + types + test    # lint first
if argv has no known task: print the usage, return 2
for cmd in TASKS[task]:
    code = run(cmd)
    if code != 0: return code
return 0
```
