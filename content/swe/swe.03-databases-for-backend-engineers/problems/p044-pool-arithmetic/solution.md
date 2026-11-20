## Approach

| Event | checked_out | checked_in | Why |
|---|---|---|---|
| checkout A to E | 1, 2, 3, 4, 5 | 0 | new connections are created on demand; the limit is 3 + 2 = 5 |
| checkout F | (5) | (0) | no idle connection and no room to create one: waits 0.2 s, then `timeout` |
| return A | 4 | 1 | A goes into the queue |
| checkout G | 5 | 0 | G takes the idle connection |
| return B and C | 3 | 2 | both go into the queue |
| return D | 2 | 3 | the queue now holds 3 idle connections |

(Checked by running the program.)

With `max_overflow=0` only 3 connections exist: the fourth checkout (`D`) would already time out. A pool protects the database from too many connections, and protects your program from opening one per request.

## Complexity

Not applicable.

## Another way

`pool.status()` prints a one-line summary: `Pool size: 3  Connections in pool: 2 Current Overflow: 2 Current Checked out connections: 3`. Its overflow counter starts at `-pool_size`, which is why the raw numbers look odd; `checkedout()` and `checkedin()` are easier to read.

## Why it matters

Sizing the pool is arithmetic: (number of workers x pool size) must stay below what the database allows (PostgreSQL defaults to 100 connections). A timeout at the sixth checkout is exactly what a busy web server shows when connections leak (problem 43) or are held too long.
