## Model answer

**The four signals.** `SIGTERM`: graceful shutdown: stop accepting connections, let the workers finish the requests that are **in flight**, then exit. `SIGINT` (Ctrl+C): a fast shutdown. `SIGHUP`: reload the configuration and restart the workers one by one without dropping connections. `SIGKILL`: the process is removed by the kernel at once. A program **cannot** catch, block or ignore `SIGKILL` (or `SIGSTOP`), so it gets no chance to finish a request, flush a buffer or release a lock. That is what an out-of-memory kill looks like too (exit code 137 = 128 + 9).

**What Docker sends.** `docker stop` sends `SIGTERM`, waits for the grace period (10 seconds by default), and **then** sends `SIGKILL` to whatever is still running. `docker kill` sends `SIGKILL` straight away, so every request in flight is cut off: "connection reset". Using it for deploys would drop requests every time.

**`graceful_timeout` and `timeout`.** `timeout` (30 seconds by default) is how long a worker may be silent **while serving** before the master kills it (`WORKER TIMEOUT`). `graceful_timeout` is how long workers get to finish after a shutdown signal. A 40-second request exceeds `timeout` and is killed mid-request, which users see as a reset; raising `timeout` to 60 only hides the problem and ties up a worker for a minute at a time. For shutdown, the grace period of the platform (`docker stop -t`, Kubernetes `terminationGracePeriodSeconds`) must be **longer** than `graceful_timeout`, or `SIGKILL` arrives first. The better fix is to move the slow work out of the request: queue it and return `202` with a status URL (swe.08), so no interactive request needs 40 seconds.

**Shell form.** With `CMD gunicorn ...` (shell form) Docker runs `/bin/sh -c "gunicorn ..."`: the shell is **PID 1** and does not forward `SIGTERM` to Gunicorn, so `docker stop` waits out the whole grace period and then kills everything. The **exec form** (`CMD ["gunicorn", ...]`) makes Gunicorn PID 1, and it receives the signal itself.

**What the app does on `SIGTERM`.** (1) Turn readiness red (set `draining`) so the load balancer stops sending new requests; (2) let the requests already **in flight** finish, within the grace period; (3) close connections and exit. Gunicorn and Uvicorn do steps 2 and 3; the application adds step 1.

**Checklist: your answer should mention**
- [ ] SIGTERM = graceful (finish in-flight requests, then exit); SIGINT = fast shutdown; SIGHUP = reload; SIGKILL = immediate
- [ ] SIGKILL cannot be caught or ignored, so no cleanup is possible (also what an OOM kill is)
- [ ] `docker stop` = SIGTERM, then SIGKILL after the grace period; `docker kill` = SIGKILL at once
- [ ] `timeout` (silent worker killed) versus `graceful_timeout` (time to finish on shutdown); the platform's grace period must be longer than `graceful_timeout`
- [ ] raising `timeout` hides the slow request; move it to a queue and answer 202
- [ ] shell-form CMD makes `sh` PID 1, which swallows SIGTERM; use the exec form
- [ ] on SIGTERM: readiness red, finish in-flight work, exit
