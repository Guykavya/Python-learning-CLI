## Hint 1

Write the script as a table with one column per dispatcher and keep the state of the outbox next to it: for each item whether it is **sent** and who **claimed** it. Do the steps in the order of the `script` list, one at a time. At each `read`, list the pending items **now**.

## Hint 2

Run 1: after D1's first `next`, item 1 is sent. D2 reads `[2, 3]`. D1 sends item 2 and D2 sends item 2 as well (it does not know D1 already did). Then both send item 3. Run 2: the same steps, but the second dispatcher to touch an item finds `claimed_by` set and skips it. Run 3: D1 claims item 2, then dies: nobody ever sends item 2, and D2 skips it because it is claimed.
