## Approach

The model answer is in `answer.md`. The method behind it: name the **bottleneck** first, then
pick the tool that removes that bottleneck.

| Workload | Bottleneck | Tool |
|---|---|---|
| 200 pages | network wait | asyncio (or threads) |
| 5,000 photos | CPU | processes |
| 2 GB log | CPU (regex), some disk | processes, chunked |
| chat server | network wait, many connections | asyncio |
| blocking weather API | network wait, blocking library | threads |
| 1,000,000 prime checks | CPU | processes |
| one tiny file | nothing | no concurrency |
| download + extract | network, then CPU | asyncio/threads, then processes |

## Check your answer

- Did you pick **processes** (not threads) for pure-Python computing, and say it is because of
  the GIL?
- Did you pick asyncio for the 3,000-connection server and say why threads cost more there?
- For the blocking library (5), did you avoid plain asyncio, or say `asyncio.to_thread`?
- Did you notice that workload 8 has two stages with different answers?
- Did you say "no concurrency" for workload 7 instead of forcing a tool onto it?

## Another way

You do not have to guess: **measure**. Time the job, then watch a CPU monitor (`top`, Task
Manager). If one core sits at 100 % the job is CPU-bound. If the CPU is near 0 % while the
program is slow, it is waiting. `cProfile` (core.20) also shows where time goes: lots of time in
`socket.recv` or `read` means I/O; lots in your own functions means CPU.
