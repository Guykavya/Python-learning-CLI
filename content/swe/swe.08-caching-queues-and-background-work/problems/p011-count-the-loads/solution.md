## Approach

Without protection, loads = requests that arrive while the first load is running = rate x load time.

| # | Rate | Load | Protection | Requests before the value is ready | Loads |
|---|---|---|---|---|---|
| 1 | 200/s (every 5 ms) | 100 ms | none | t = 0, 5, ..., 95 | 20 |
| 2 | 200/s | 100 ms | single flight | only the first loads | 1 |
| 3 | 50/s (every 20 ms) | 100 ms | none | t = 0, 20, 40, 60, 80 | 5 |
| 4 | 1000/s (every 1 ms) | 250 ms | none | t = 0 .. 249 | 250 |
| 5 | 10/s (every 100 ms) | 50 ms | none | t = 0 only | 1 |
| 6 | 400/s (every 2.5 ms) | 100 ms | none | t = 0, 2.5, ..., 97.5 | 40 |

This is Little's law (chapter 15.3): the number of requests "in flight" = arrival rate x time. Doubling the rate doubles the stampede (line 6). In a real system it is worse than the simulation: 20 loads at once make the database slower, the window grows, and even more requests pile in.

## Cost

The simulation is O(rate x duration) steps; the formula is O(1).

## Another way

Run the threaded version from chapter section 6.1 (`get_naive` with 20 threads and a `Barrier`). It gives "many" loads instead of an exact number, because the threads' timing varies. That is why this problem uses a deterministic simulation.
