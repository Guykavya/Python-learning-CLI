## Approach

Apply the two questions from Hint 1 to each line.

| # | Answer | Why |
|---|---|---|
| 1 | cache | the same expensive read, very often; a price that is a minute old is fine (and the order itself checks the database) |
| 2 | queue | 10,000 sends are slow and unreliable; answer "sending" at once and let workers do it |
| 3 | both | building is slow work for a queue; the finished report is then served from a cache (or a stored file) all month |
| 4 | neither | must be exact now; a stale "not used" lets the coupon be used twice. A unique index in the database is the truth |
| 5 | queue | slow work after the upload; show "processing" until it is done |
| 6 | cache | read constantly, changes almost never |
| 7 | neither | money: show the real balance from the database; the withdrawal itself must check it in a transaction |
| 8 | both | the scheduled job (queue) calls the limited API once an hour; pages read the rates from the cache |

## Cost

Reading only. In a design review, this question is asked before any code is written.

## Another way

Write a small "staleness budget" table (chapter section 5.4) for the data in each situation. Data whose budget is "none" is never served from a cache; work whose result the user needs "now" is never put on a queue.
