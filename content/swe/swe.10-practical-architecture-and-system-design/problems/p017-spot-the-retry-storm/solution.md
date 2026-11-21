## Approach

| Configuration | Calculation | Database calls | Time |
|---|---|---|---|
| every layer retries 3 times | 3 x 3 x 3 | **27** | 27 s |
| retries only at the edge `[3, 1, 1]` | 3 x 1 x 1 | **3** | 3 s |
| A and B retry, C does not `[3, 3, 1]` | 3 x 3 x 1 | **9** | 9 s |
| every layer retries, 10 s budget | the clock reaches 10 after 10 database calls; every layer then refuses to start another attempt | **10** | 10 s |

This is the chapter's answer to "Try it: spot the retry storm": **retry in one place only** (usually the outermost caller, or the layer that knows the operation is idempotent), add a **circuit breaker** on the database calls, and add **jitter** so that clients do not retry in step. The deadline version shows the other half of the cure: even when several layers do retry, a shared **time budget** puts a ceiling on the damage (10 calls instead of 27, and the budget is also the time the user waits). Overloaded dependencies recover only if callers back off.

## Cost

Reading only. The program is the arithmetic of section 12.2 made executable: change `attempts` or the deadline and predict the output first.

## Another way

Pass the remaining budget down as a parameter ("you have 800 ms left") instead of a shared clock, which is how real systems propagate a deadline through several services.
