## Hint 1

Run the tests and read which keys fail. For each failing key ask: what does the definition in the table say, and what does the code actually compute?

## Hint 2

Three things to check, one per wrong key: which attribute is passed to `durbin_watson`? which threshold is used for leverage (`p/n` or `2p/n`)? which column names does the VIF loop skip?
