## Hint 1

Every time a child process starts, ask two questions. Which top-level lines run again in the
child (and what is `__name__` there)? What is in the **child's** `items` when `child(tag)` is
called: the parent's list, or the list built by the child's own import? And `child("main")`,
with no `Process` around it: which process runs that?

## Hint 2

Keep one `items` column per process:

```
parent:  ['start'] -> append 'parent' -> ['start', 'parent']
child 1: import again -> ['start'] -> append 'one' -> prints ['start', 'one'] -> exits
parent:  unchanged by child 1
parent:  child("main") is a plain call -> appends to the PARENT's list
child 2: import again -> ['start'] -> append 'two'
```
