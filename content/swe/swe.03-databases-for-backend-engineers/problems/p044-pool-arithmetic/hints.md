## Hint 1

Five checkouts in a row: the pool creates a new connection each time (nothing idle yet), up to 3 + 2 = 5. The counts are simply `checked_out` 1, 2, 3, 4, 5 and `checked_in` 0.

## Hint 2

The sixth request finds none idle and no room to create one, so it waits `timeout` and fails: the line is `checkout F: timeout`. Then A is returned: it goes into the queue (checked_in 1).

## Hint 3

`G` takes the idle one (checked_out 5, checked_in 0). Returning B and C puts two into the queue (checked_in 2, checked_out 3). Returning D: the queue has room for a third idle connection (3): checked_in 3, checked_out 2.
