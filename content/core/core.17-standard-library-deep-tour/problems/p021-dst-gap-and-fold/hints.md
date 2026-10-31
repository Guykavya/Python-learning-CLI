## Hint 1

For each line, first ask: is this wall time *ordinary* (happens once), in the *gap* (never
happens) or in the *fold* (happens twice)? For an ordinary time the offset is simply the one in
force on that date. Where are `C` (02:30 on 10 March) and `H` (01:30 on 3 November)?

## Hint 2

Gap with `fold=0`: use the offset from *before* the jump (EST, -05:00). Then for `D` turn that
into UTC by hand: 02:30 at -05:00 is 07:30 UTC. Is 07:30 UTC before or after the jump (02:00 EST
is 07:00 UTC)? Which offset applies there, and what does the wall clock show?

## Hint 3

For `F` and `G`: `later` was made by adding one day to the *wall clock*. Same `tzinfo` on both
sides means the subtraction compares wall clocks: how far apart are they? Then do it in UTC:
09:00 EST is 14:00 UTC, 09:00 EDT is 13:00 UTC.

## Hint 4

For `L` to `N`, the fall-back jump happens at 02:00 EDT, which is 06:00 UTC. 05:30 UTC is before
it (EDT, the first 01:30), 06:30 UTC is after it (EST, the second 01:30, so `fold` is 1).
For London on 31 March the jump is at 01:00 GMT = 01:00 UTC.
