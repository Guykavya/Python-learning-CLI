## Approach

The model answer is in `answer.md`. The thread running through it: **a stop is a request with a deadline**. `SIGTERM` is the request, the grace period is the deadline, `SIGKILL` is what happens at the deadline. A good deployment makes sure the process (1) hears the request (exec form, PID 1), (2) can finish its work in time (short requests, `graceful_timeout`, a long enough platform grace period) and (3) tells the load balancer to stop sending traffic first (readiness red).

## Cost

Nothing to build; the cost of getting it wrong is dropped requests on every deploy and `WORKER TIMEOUT` lines that appear only when a slow request meets a deploy.

## Another way

You can see the signal for yourself without Docker: start `gunicorn` with a one-line app that sleeps for 5 seconds, send it `kill -TERM <pid>` while a request runs, and watch the request finish before the process exits (chapter 2.3). Then repeat with `kill -9`: the request dies. (Commands are in the chapter's tutorial; run them on your machine.)
