## Hint 1

`count` is `[2, 1, 3]`: two records have key 0 (bob, eli), one has key 1 (dee), three have key 2 (ann, cy, fay).

## Hint 2

`start` is `[0, 2, 3]`: key 0 begins at slot 0, key 1 at slot 2 (after the two zeros), key 2 at slot 3.

## Hint 3

Process in order: ann (key 2) goes to slot 3, then `start[2]` becomes 4; bob (key 0) goes to slot 0; cy goes to slot 4; and so on.
