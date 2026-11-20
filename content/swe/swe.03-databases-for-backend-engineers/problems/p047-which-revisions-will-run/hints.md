## Hint 1

First draw the chain and mark the current revision. Going up means "the revisions to the right"; going down means "the revisions to the left, newest first".

## Hint 2

The target of a `downgrade` is the revision you **end up at**: its own `downgrade()` does not run (the state "0002 applied" is exactly what you want to keep).

## Hint 3

Case 3: from 0004 you want to end at 0002, so undo 0004, then 0003. Case 5: to reach `base` you undo everything that is applied: 0003, 0002, 0001. Case 4: from nothing, apply 0001, 0002, 0003.
