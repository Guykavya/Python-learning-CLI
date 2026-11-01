## Hint 1

Keep a small table with the counter value, and a list `done`. For every `set`, both watchers
run in order: first the logger, then the "big" check. Which `set` calls does the program make
in the first loop? In the undo loop, which command is popped first (last in, first out)?

## Hint 2

```
loop 1:  do +4  -> set(4)    log 0->4
         do +7  -> set(11)   log 4->11, big!
         do -2  -> set(9)    log 11->9
print value: 9
strategies on 9: double, negate, lambda
undo loop: while done has MORE than one command: pop last and undo ...
after the loop: one command is left. A watcher is removed, then it is undone.
```
The `lambda` has `__name__ == "<lambda>"`, so the program prints the word `lambda`.
