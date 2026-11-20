## Approach

| Setting | What happens |
|---|---|
| read timeout 1.0 s | every gap is 0.8 s < 1.0 s: the timeout never fires; the answer is complete at 8.0 s |
| read timeout 0.5 s | the first gap, 0.8 s, is longer than 0.5 s: gives up at 0.5 s with 0 bytes |
| timeout 1.0 s + deadline 3.0 s | bytes at 0.8, 1.6, 2.4; then only 0.6 s are left, the next byte needs 0.8 s: gives up at 3.0 s with 3 bytes |
| timeout 1.0 s + deadline 10.0 s | the deadline is far away; done at 8.0 s with 10 bytes |

Output (checked by running the code):

```text
read timeout 1.0 s: done at 8.0s with 10 bytes
read timeout 0.5 s: timeout after 0.5s with 0 bytes
timeout 1.0 s, deadline 3.0 s: timeout after 3.0s with 3 bytes
timeout 1.0 s, deadline 10.0 s: done at 8.0s with 10 bytes
```

A **read timeout** limits each single wait, and every received byte restarts the clock. A server that drips one byte every 0.8 s never triggers it, however long the answer takes: this is the "slow loris" behaviour. Only a **total deadline** limits the whole operation.

## Complexity

Not applicable.

## Another way

In `httpx`, `Timeout(read=1.0)` is a per-wait timeout; for a hard total limit you need a deadline of your own (check `time.monotonic()` while reading a streamed body, or `asyncio.timeout`).

## Why it matters

A client with only a read timeout can still hang for minutes on a server that trickles data. Know which of the two limits you have set (chapter section 20.3).
