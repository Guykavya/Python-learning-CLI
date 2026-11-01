## Hint 1

Trace `reverse_all` for the plain stack first: push 1, 2, 3 then pop until empty gives
`[3, 2, 1]`; `expected` is `list(reversed(items))`, so it prints `ok`. Now, for each subclass, ask
what its `push` does differently. Does it ever raise? Does it ever skip the append? Remember
`check` catches *any* exception and prints only its class name.

## Hint 2

```
LimitedStack(3), 3 items      -> never full when pushing: ok
LimitedStack(2), 3 items      -> the 3rd push raises OverflowError, check prints "raised ..."
DedupStack [1,2,3]            -> no repeats, so ok
DedupStack [1,2,1]            -> the second 1 is skipped: pops give [2, 1], expected [1, 2, 1]
CountingStack                 -> same results as Stack, plus a counter (pushes = 2)
FrozenStack [1]               -> push raises TypeError ; with [] there is nothing to push
Last 5 lines: issubclass is True for all; "push is Stack.push" is True only for Stack
              (CountingStack, LimitedStack, DedupStack, FrozenStack each define their own push)
```
