# Signals and graceful shutdown

Chapter sections 2.6 (signals: how processes are told what to do) and 5.5 (`SIGTERM` again), and "Try it: why did the request die?". A report endpoint of a Gunicorn app sometimes takes 40 seconds. During a deploy, users on large reports see "connection reset", and the Gunicorn log has `WORKER TIMEOUT` on some days and nothing on others. A teammate proposes: "raise `timeout` to 60 and use `docker kill` to stop the old containers faster".

In `answer.md` explain (about 200 to 350 words):

1. What `SIGTERM`, `SIGINT`, `SIGHUP` and `SIGKILL` each do to Gunicorn (one line each), and which of them the program **cannot** handle, and why.
2. Which signal does `docker stop` send first, and what happens after the grace period if the process is still running? What does `docker kill` do instead?
3. What `graceful_timeout` protects, and how it differs from `timeout`. Why does a **long request** make shutdown slow, and what is the better long-term fix for a 40-second report?
4. Why does a container whose `CMD` is in **shell form** often ignore `docker stop` (what is PID 1)?
5. What should the application do when it receives `SIGTERM`, in order? (three steps)

Use the words *graceful*, *in flight*, *drain*, *PID 1*, *exec form*.

## Example

A good line for part 2: "`docker stop` sends `SIGTERM`, waits (10 seconds by default), then sends `SIGKILL`."
