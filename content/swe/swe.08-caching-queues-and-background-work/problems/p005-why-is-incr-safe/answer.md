## Model answer

**The lost update.** Version 1 is a *read-modify-write* done in two separate commands:

```text
t1  A: GET hits -> "41"
t2  B: GET hits -> "41"
t3  A: SET hits 42
t4  B: SET hits 42        <- two visits, but the counter moved by one
```

Both servers read before either wrote, so B overwrote A's work: a **lost update**. Nothing failed and nothing was logged; the number is simply wrong, and the error grows with traffic.

**Why `INCR` is safe.** Redis executes commands **one at a time** on a single thread. `INCR hits` reads, adds and writes **inside one command**, so it is **atomic**: no other client's command can run between its read and its write. Two `INCR`s from two servers are queued and applied one after the other: 42, then 43.

**Why a Python lock does not help.** A `threading.Lock` lives in one process's memory. Server B on another machine never sees it. To make version 1 safe you would need a lock shared by all servers, which is a much heavier (and riskier) tool than one atomic command. Put the operation where the data is.

**The same idea elsewhere.** SQL: `UPDATE counters SET n = n + 1 WHERE id = 1` (the database does the read and the write in one statement). Django: `Counter.objects.filter(pk=1).update(n=F("n") + 1)`.

**`INCR` then `EXPIRE`.** If the process dies between the two commands, the key never gets an expiry, and a fixed-window rate-limit key lives for ever (with a fixed key name, the user is blocked for ever). Fix: `SET key 0 EX window NX` first (create-with-expiry in one atomic command), then `INCR`, which keeps the existing TTL. In real Redis a Lua script or `MULTI/EXEC` also works.

**Checklist: your answer should mention**
- [ ] a timeline where both servers read 41 before either writes, ending at 42 instead of 43
- [ ] the name: read-modify-write across two commands causes a lost update
- [ ] Redis runs one command at a time (single-threaded), so one command is atomic
- [ ] `INCR` does the read, the add and the write inside one command
- [ ] an in-process lock cannot coordinate separate processes or machines
- [ ] SQL `SET n = n + 1` and Django `F("n") + 1` are the same idea
- [ ] `INCR` + `EXPIRE` can be split by a crash; `SET ... NX EX` first (or Lua / `MULTI`) closes the gap
