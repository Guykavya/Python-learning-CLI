# Which metric type?

Chapter sections 10.1 (logs tell stories, metrics tell trends) and "Try it: which metric type?". Prometheus has three types for what you measure:

| Type | What it is | Typical question |
|---|---|---|
| **counter** | a number that only goes **up** (it resets to 0 when the process restarts); you look at its **rate** | how many per second? |
| **gauge** | a number that goes **up and down** | what is the value **right now**? |
| **histogram** | counts of observations in **buckets** (plus a sum and a count) | how are the **durations or sizes distributed**? what is the p95? |

For each thing below write `counter`, `gauge` or `histogram`. No program is shown; this is a reading exercise.

1. The number of requests served since the process started.
2. The number of jobs waiting in the queue.
3. How long it takes to render a report.
4. The memory the process uses at this moment.
5. The number of requests that ended with an error (status 500 to 599).
6. The number of jobs being processed right now.
7. The bytes sent to clients since the process started.
8. The size of each uploaded file, to see whether 95% of uploads are under 5 MB.

## Answer format

Write exactly eight lines, one per item, in this form (number, colon, space, one word):

```text
1: counter
2: gauge
...
8: histogram
```

## After you answer

- Which of the eight would you graph as a **rate** (per second), and which as a **level**?
- The service of the chapter exposes `http_requests_in_flight`. Which type is it, and why would it be wrong as a counter?
