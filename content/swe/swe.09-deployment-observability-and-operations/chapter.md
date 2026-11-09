# Chapter 9 (SWE): Deployment, observability and operations

Writing code that works on your laptop is half of the job. The other half is **running it**: starting it reliably, configuring it for different places, keeping it alive, finding out when it is unhealthy, shipping new versions without breaking users, going back when a release is bad, and recovering when data is lost. This is called **operations**, and the tools for it (Docker, Nginx, CI, Prometheus and friends) are the part of software engineering that most beginners never see until their first real job.

This chapter is built differently from the earlier ones. Almost every section is a **hands-on tutorial for a real tool**. You will install it, run it, break it on purpose and fix it. The outputs shown are real: they were captured on a real machine by actually running the commands.

By the end you reach two outcomes, both practised on a real running system:

- You can **trace one failing request through the logs using its request ID**: from the browser-facing proxy, through the application, to the exact line of the traceback (section 8).
- You can **roll back a bad deployment**: ship a broken release, watch it fail its health check, and return to the last good version, automatically and by hand (section 12).

You will also learn to build a container image, run several containers together, put a reverse proxy in front, write structured logs, expose health checks and metrics, let CI test and build every change, take backups and **prove they restore**.

Prerequisites: swe.01 (the terminal, git), swe.02 (HTTP), swe.05 (FastAPI), swe.07 (secrets, health of the system under attack) and swe.08 (workers, graceful shutdown). The project you build in swe.04, swe.05 or swe.06 can be dockerised with exactly the steps here.

> **How to follow this chapter.** Type the commands yourself. Each tutorial says what you should see; if your output differs only in IDs, times or addresses, that is normal (the text says when). A **Try it on your machine** note marks steps whose output depends on something outside this book (your cloud account, your GitHub repository, a real server). Those are described with exact commands, but no output is shown for them.
>
> **Safety rules used in this chapter.** Everything we start has a name that begins with `pbtut` (for "Pagebound tutorial") and listens on a high port (18000 and up) on `127.0.0.1` only, so it cannot clash with other projects on your machine or be reached from outside. Cleanup commands in the text only touch those names. **Never run `docker system prune` or `docker rm $(docker ps -aq)` casually**: they delete things that belong to your other projects.

Every output block was produced by running the code above it, with these versions (patch versions may differ):

```bash run
python --version
docker --version
docker compose version
jq --version
curl --version | head -1 | cut -c1-14
git --version
```
```text
Python 3.14.4
Docker version 29.9.1, build dfc520d
Docker Compose version v5.6.0
jq-1.8.1
curl 8.18.0 (x
git version 2.53.0
```

## Table of contents

1. [The operations mindset](#1-the-operations-mindset)
2. [Running Python web apps for real: Gunicorn and Uvicorn](#2-running-python-web-apps-for-real-gunicorn-and-uvicorn)
3. [Configuration from the environment](#3-configuration-from-the-environment)
4. [Docker, step by step](#4-docker-step-by-step)
5. [Dockerising the Pagebound service](#5-dockerising-the-pagebound-service)
6. [Docker Compose: several containers as one system](#6-docker-compose-several-containers-as-one-system)
7. [Nginx: the front door](#7-nginx-the-front-door)
8. [Structured logs and request IDs](#8-structured-logs-and-request-ids)
9. [Health checks](#9-health-checks)
10. [Metrics and monitoring with Prometheus](#10-metrics-and-monitoring-with-prometheus)
11. [Continuous integration with GitHub Actions](#11-continuous-integration-with-github-actions)
12. [Deploying and rolling back](#12-deploying-and-rolling-back)
13. [Backups and restore drills](#13-backups-and-restore-drills)
14. [Operating it: runbooks, incidents and routine care](#14-operating-it-runbooks-incidents-and-routine-care)
15. [Project: Dockerise, deploy and monitor your API with CI](#15-project-dockerise-deploy-and-monitor-your-api-with-ci)
16. [Common traps](#16-common-traps)
17. [Collected traps](#17-collected-traps)
18. [Summary](#18-summary)

## 1. The operations mindset

### 1.1 What changes between your laptop and production

| On your laptop | In production |
|---|---|
| you start the program by hand | something starts it, restarts it if it crashes, and starts it after a reboot |
| one user (you) | many users at once, some of them hostile |
| settings are in the code or a file you edited | settings differ per environment and secrets must not be in the code |
| you read errors in the terminal | nobody is watching a terminal; logs must be collected and searchable |
| you notice when it breaks | it breaks at 3 a.m.; something must notice and tell someone |
| you restart it to deploy | users must not notice a deployment; a bad one must be undone |
| a lost file is annoying | lost data is a disaster; backups must exist **and be known to restore** |

Operations is the work of closing those gaps. The goal is not heroics; it is a system that is **boring to run**: predictable deployments, health that is visible, failures that are small and recoverable.

### 1.2 Environments

| Environment | Purpose | Typical difference |
|---|---|---|
| **Development** | you write code | debug mode, small data, hot reload |
| **Test / CI** | automatic checks on every change | throw-away, repeatable, no real secrets |
| **Staging** | a copy of production for a last check | same image, same settings shape, fake data |
| **Production** | real users | real data, real secrets, monitoring, backups |

The more alike they are, the fewer surprises ("it worked in staging"). The single most useful rule is **build once, deploy many**: you build one artifact (a Docker image tagged with a version) and run the *same* artifact in staging and production; only the **configuration** you inject differs. If you rebuild for each environment, then what you tested is not what you shipped.

### 1.3 Twelve-factor, the short version

The "twelve-factor app" (a long-standing guide to cloud-friendly applications) turns into a handful of habits that this chapter practises:

1. **One codebase** in version control, many deployments of it.
2. **Declare dependencies** exactly (`requirements.txt` with pinned versions).
3. **Configuration in the environment**, not in the code (section 3).
4. Treat backing services (database, Redis) as **attached resources** reached by a URL from the configuration.
5. **Separate build, release and run**: build an image, combine it with config into a release, run it.
6. Run the app as **stateless processes**; keep state in databases and volumes.
7. **Export services by port**: the app listens on a port and a proxy sits in front.
8. **Scale out with processes**: run more copies, not a bigger single process.
9. **Disposable**: fast start, graceful stop (`SIGTERM`); crashing must be safe.
10. **Keep environments similar.**
11. **Logs are an event stream** written to standard output; the platform collects them (section 8).
12. **Run admin tasks** (migrations, one-off scripts) as one-off processes of the same image.

### 1.4 The tools in this chapter

| Tool | Its job | Section |
|---|---|---|
| **Gunicorn**, **Uvicorn** | run your Python web app as a pool of server processes | 2 |
| **Environment variables**, `.env` files | configuration and secrets | 3 |
| **Docker** | package the app and everything it needs into an *image*, run it as an isolated *container* | 4, 5 |
| **Docker Compose** | describe and run several containers together (app, cache, proxy) | 6 |
| **Nginx** | the reverse proxy in front: TLS, load balancing, rate limits | 7 |
| **Structured logging**, `jq` | logs a machine can search; one request id per request | 8 |
| **Health checks** | tell the platform whether the app is alive and ready | 9 |
| **Prometheus** | collect and query numbers (requests, errors, latency); alert | 10 |
| **GitHub Actions** | run tests and build the image on every change | 11 |
| **Deploy scripts** | release a version, verify it, roll back | 12 |
| **`pg_dump`**, the SQLite backup API | backups and restore drills | 13 |

### 1.5 Install what you need

You need these on your own computer. Check each with the version command shown above.

| Tool | Install | Check |
|---|---|---|
| **Docker Engine + Compose** | Linux: follow the official guide for your distribution at `docs.docker.com/engine/install` (it is a short copy-paste list, and the *Compose plugin* comes with it). macOS and Windows: install Docker Desktop. | `docker --version`, `docker compose version`, then `docker run --rm hello-world` |
| **curl** | already on macOS and most Linux; Windows 10+ has it | `curl --version` |
| **jq** (reads JSON in the terminal) | `sudo apt install jq` / `brew install jq` / `winget install jqlang.jq` | `jq --version` |
| **git** | from your package manager | `git --version` |
| **Gunicorn** | `pip install gunicorn` (inside your virtual environment) | `gunicorn --version` |
| **Nginx, Redis, PostgreSQL, Prometheus** | **do not install these**: we run them as containers | n/a |

On Linux, Docker needs permission to use its socket. The usual way is `sudo usermod -aG docker $USER` and logging in again. Be aware that the `docker` group is effectively **root** on that machine: anyone who can run Docker can read or change any file. On Windows, run these tutorials in WSL 2 (a Linux shell) so that the commands match the text.

Two last rules for the chapter: Docker commands need the Docker daemon running (`docker info` shows an error if it is not), and everything we start can be removed with the cleanup block at the end of each tutorial.

## 2. Running Python web apps for real: Gunicorn and Uvicorn

### 2.1 What a server process does

`flask run` and `uvicorn --reload` are **development** tools: single process, automatic reload, helpful error pages. In production you need a **server** that accepts connections, passes requests to your code, manages several worker processes, restarts workers that die, and shuts down cleanly. For Python the standards are:

- **WSGI** servers for synchronous frameworks (Flask, Django): **Gunicorn** (also uWSGI, Waitress).
- **ASGI** servers for async frameworks (FastAPI, Starlette, Django async): **Uvicorn** (also Hypercorn, Daphne).

You met WSGI and ASGI as protocols in swe.02 and swe.04. This section is about the programs that speak them.

### 2.2 Gunicorn's pre-fork model

Gunicorn starts one **master** process that does no request work. It **forks** several **worker** processes; each worker handles requests. The master watches them: a worker that dies or hangs is killed and replaced.

```text
             gunicorn master   (listens on the port, manages workers, handles signals)
                 |
     +-----------+-----------+
     |           |           |
  worker 1    worker 2    worker 3     (each runs your app code, one request at a time for "sync" workers)
```

Because a *sync* worker handles **one request at a time**, the number of workers is your concurrency. With `--threads N` each worker runs N threads (the `gthread` worker class). Async worker classes exist for many concurrent connections.

### 2.3 Tutorial: Gunicorn, hands on

A tiny Flask application with two endpoints, one that reports the process id and one that sleeps:

```python
# wsgi_demo.py
import os
import time

from flask import Flask, request

app = Flask(__name__)


@app.get("/pid")
def pid():
    return {"pid": os.getpid()}


@app.get("/slow")
def slow():
    seconds = float(request.args.get("seconds", "0.1"))
    time.sleep(seconds)
    return {"slept": seconds, "pid": os.getpid()}
```

Instead of a long command line, put the settings in a Python file, which can be committed and reviewed:

```python
# gunicorn.conf.py
bind = "127.0.0.1:18001"           # listen on this machine only; a proxy (section 7) faces the world
workers = 2                         # worker processes
timeout = 2                         # kill a worker that spends more than 2 seconds on one request
graceful_timeout = 5                # on shutdown, wait up to 5 s for requests to finish
pidfile = "gunicorn.pid"
accesslog = "-"                     # "-" means standard output
errorlog = "-"
loglevel = "info"
```

Start it in the background and look at the processes it created:

```bash run
gunicorn --version
gunicorn -c gunicorn.conf.py wsgi_demo:app > gunicorn.log 2>&1 &
sleep 2
master=$(cat gunicorn.pid)
echo "master pid file written: $([ -n "$master" ] && echo yes)"
echo "worker processes (children of the master): $(ps --ppid "$master" -o pid= | wc -l)"
curl -s localhost:18001/pid
```
```text
gunicorn (version 26.2.0)
master pid file written: yes
worker processes (children of the master): 2
{"pid":91881}
```

`wsgi_demo:app` means "in the module `wsgi_demo`, the object `app`". The `pid` in the reply belongs to **one worker**. Now the proof that workers are the unit of concurrency: two slow requests at once land on two different workers, and a third has to wait.

```bash run
echo "--- two simultaneous requests:"
( curl -s "localhost:18001/slow?seconds=0.5" & curl -s "localhost:18001/slow?seconds=0.5" & wait ) | jq -sc '{distinct_workers: (map(.pid) | unique | length)}'
echo "--- three simultaneous requests, only two workers:"
start=$(date +%s.%N)
( for i in 1 2 3; do curl -s "localhost:18001/slow?seconds=0.5" & done; wait ) > /dev/null
end=$(date +%s.%N)
python3 -c "print('the third request waited for a free worker, so it took at least 1 s:', $end - $start >= 1.0)"
```
```text
--- two simultaneous requests:
{"distinct_workers":2}
--- three simultaneous requests, only two workers:
the third request waited for a free worker, so it took at least 1 s: True
```

(Timing differs by machine; the comparison is what matters.) Next, two things operators do constantly. First a **graceful reload** with `SIGHUP`: the master starts new workers with your new code, then retires the old workers once they finish their current requests. The master process and the listening port are never closed, so no request is refused:

```bash run
master=$(cat gunicorn.pid)
before=$(ps --ppid "$master" -o pid= | sort | tr -d ' ' | tr '\n' ' ')
kill -HUP "$master"
sleep 2
after=$(ps --ppid "$master" -o pid= | sort | tr -d ' ' | tr '\n' ' ')
echo "master still the same process : $(kill -0 "$master" && echo yes)"
echo "all workers replaced           : $([ "$before" != "$after" ] && echo yes)"
echo "service answered during/after  : $(curl -s -o /dev/null -w '%{http_code}' localhost:18001/pid)"
grep -E "Handling signal|Booting worker|Worker exiting" gunicorn.log | sed -E 's/^\[[^]]*\] \[[0-9]+\] //; s/pid: [0-9]+/pid: N/' | sort | uniq -c
```
```text
master still the same process : yes
all workers replaced           : yes
service answered during/after  : 200
      4 [INFO] Booting worker with pid: N
      1 [INFO] Handling signal: hup
      2 [INFO] Worker exiting (pid: N)
```

Second, the **timeout**. A request that takes longer than `timeout` makes the master kill that worker (its code may be stuck) and start a new one. The client gets an error instead of its answer (Gunicorn 26 answers HTTP 500 here; other versions simply drop the connection), and the log shows what happened:

```bash run
curl -s -m 10 -o /dev/null -w "client saw: exit code %{exitcode}, http code %{http_code}\n" "localhost:18001/slow?seconds=5" ; true
sleep 1
grep -E "WORKER TIMEOUT|Booting worker" gunicorn.log | tail -3 | sed -E 's/^\[[^]]*\] \[[0-9]+\] //; s/pid:[ ]?[0-9]+/pid:N/'
echo "service still healthy afterwards: $(curl -s -o /dev/null -w '%{http_code}' localhost:18001/pid)"
```
```text
client saw: exit code 0, http code 500
[INFO] Booting worker with pid:N
[CRITICAL] WORKER TIMEOUT (pid:N)
[INFO] Booting worker with pid:N
service still healthy afterwards: 200
```

Finally, the **graceful stop** with `SIGTERM`, which is what a deployment tool or Docker sends first:

```bash run
master=$(cat gunicorn.pid)
workers=$(ps --ppid "$master" -o pid= | tr -d ' ' | tr '\n' ' ')
kill -TERM "$master"
sleep 2
alive=0
for p in $master $workers; do kill -0 "$p" 2>/dev/null && alive=$((alive + 1)); done
echo "processes still alive: $alive"
grep -E "Handling signal: term|Shutting down|Worker exiting" gunicorn.log | sed -E 's/^\[[^]]*\] \[[0-9]+\] //; s/pid: [0-9]+/pid: N/' | sort | uniq -c
```
```text
processes still alive: 0
      1 [INFO] Handling signal: term
      1 [INFO] Shutting down: Master
      5 [INFO] Worker exiting (pid: N)
```

### 2.4 The settings that matter

| Setting | Meaning | Guidance |
|---|---|---|
| `workers` | number of worker processes | for sync workers start near `2 x CPU cores + 1`; more workers means more memory, since each loads your whole app |
| `worker_class` | `sync` (default), `gthread`, `gevent`, or an ASGI worker | `sync` for CPU or quick requests; `gthread` for I/O-bound with `threads = 4` |
| `bind` | address and port | `127.0.0.1` behind a proxy; `0.0.0.0` inside a container |
| `timeout` | seconds before a stuck worker is killed | the longest legitimate request, plus margin; **not** a request limit for slow clients |
| `graceful_timeout` | time to finish requests on shutdown | longer than your slowest request |
| `max_requests`, `max_requests_jitter` | restart a worker after N requests (plus a random amount) | a cheap defence against slow memory leaks |
| `preload_app` | import the app once in the master, then fork | saves memory (copy-on-write) and catches import errors at start-up; but a `HUP` reload then does not pick up new code |
| `keepalive` | seconds to keep idle connections | small when a proxy talks to Gunicorn |
| `accesslog`, `errorlog` | where logs go | `"-"` (stdout) in containers |

### 2.5 Uvicorn for ASGI apps

FastAPI applications run on **Uvicorn**. The development command you know is `uvicorn app:app --reload`. In production you drop `--reload` and decide how to get several processes. Uvicorn has its own supervisor:

```python
# asgi_demo.py
import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/pid")
def pid():
    return {"pid": os.getpid()}
```

```bash run
uvicorn asgi_demo:app --host 127.0.0.1 --port 18002 --workers 2 > uvicorn.log 2>&1 &
supervisor=$!
sleep 3
echo "server processes started: $(grep -c 'Started server process' uvicorn.log)   (plus the supervisor that manages them)"
grep -E "Started parent process|Started server process|Application startup complete|Uvicorn running" uvicorn.log | sed -E 's/\[[0-9]+\]/[N]/' | sort | uniq -c
curl -s localhost:18002/pid
kill -TERM "$supervisor"
sleep 2
echo "supervisor still alive: $(kill -0 "$supervisor" 2>/dev/null && echo yes || echo no)"
```
```text
server processes started: 2   (plus the supervisor that manages them)
      2 INFO:     Application startup complete.
      1 INFO:     Started parent process [N]
      2 INFO:     Started server process [N]
      1 INFO:     Uvicorn running on http://127.0.0.1:18002 (Press CTRL+C to quit)
{"pid":92010}supervisor still alive: no
```

There are two common ways to run FastAPI for real:

1. **One Uvicorn process per container, many containers** (`--workers 1`, scale with `docker compose --scale` or an orchestrator). Health checks, logs and metrics are per container and easy to reason about. This is what the rest of the chapter does.
2. **Gunicorn managing Uvicorn workers** (`gunicorn -k uvicorn_worker.UvicornWorker app:app`, with `pip install uvicorn-worker`), which gives Gunicorn's mature process management (max-requests, graceful reload) on a single machine. Older tutorials write `uvicorn.workers.UvicornWorker`; that class was moved out of Uvicorn into the separate `uvicorn-worker` package.

For both, behind a proxy, tell Uvicorn to trust the proxy's forwarded headers: `--proxy-headers --forwarded-allow-ips="<proxy address>"`. Without it the app sees the proxy's address as every client's address (the rate-limit trap of swe.07 section 11.3).

### 2.6 Signals: how processes are told what to do

| Signal | Sent by | Gunicorn does |
|---|---|---|
| `SIGTERM` | `kill`, Docker stop, systemd, Kubernetes | graceful shutdown: finish requests, then exit |
| `SIGINT` (Ctrl+C) | the terminal | fast shutdown |
| `SIGHUP` | `kill -HUP` | reload configuration and workers gracefully |
| `SIGTTIN` / `SIGTTOU` | `kill` | add or remove one worker |
| `SIGKILL` | `kill -9`, an out-of-memory kill | cannot be caught: the process vanishes at once |

Remember the lesson of swe.08: a process that receives `SIGKILL` gets no chance to clean up, so deployments should always try `SIGTERM` first and allow time.

### 2.7 Without Docker: systemd

On a plain Linux server, **systemd** starts services at boot and restarts them if they crash. You describe the service in a *unit file*:

```ini
# /etc/systemd/system/pagebound.service
[Unit]
Description=Pagebound API
After=network.target

[Service]
User=pagebound
WorkingDirectory=/srv/pagebound
EnvironmentFile=/etc/pagebound.env
ExecStart=/srv/pagebound/.venv/bin/gunicorn -c gunicorn.conf.py wsgi_demo:app
Restart=on-failure
RestartSec=2
KillSignal=SIGTERM
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
```

> **Try it on your machine** (needs a Linux server where you have `sudo`; not run here):
>
> ```bash
> sudo systemctl daemon-reload
> sudo systemctl enable --now pagebound        # start now, and at every boot
> systemctl status pagebound                    # active (running), the main PID, the last log lines
> journalctl -u pagebound -f                    # follow its logs
> sudo systemctl reload pagebound               # only if the unit defines ExecReload (kill -HUP $MAINPID)
> ```
>
> `status` prints a block that starts with `● pagebound.service - Pagebound API` and a line `Active: active (running) since ...`. Kill the main process with `sudo kill -9 <pid>` and see systemd start a new one after `RestartSec`. Docker's `restart: unless-stopped` (section 6) does the same job for containers.

### Try it: how many workers?

An app runs on a 4-core machine with Gunicorn sync workers. Each request spends 90% of its time waiting for a database. With 9 workers you measure 100% CPU idle most of the time and users complain about slowness at peak. What is the problem, and what are two ways out?

<details><summary>Answer</summary>

Each sync worker handles one request at a time, so with 9 workers only 9 requests are in flight; the other requests queue while the CPU sits idle waiting on the database. Ways out: use threads (`worker_class = "gthread"`, `threads = 4` gives 36 concurrent requests) or an async framework and server, so one process juggles many waiting requests; and/or add workers if memory allows (more processes, with a connection pool sized to match). The formula `2 x cores + 1` is a starting point for CPU-bound code, not a law.

</details>

### Try it: why did the request die?

A report endpoint sometimes takes 40 seconds. Users see "connection reset" on the large reports, and the Gunicorn log has `WORKER TIMEOUT`. What happened, and what is the right fix: raising `timeout` to 60?

<details><summary>Answer</summary>

The worker exceeded `timeout` (30 s by default), so the master killed it mid-request. Raising `timeout` hides the problem and ties up workers for a minute each. The right fix is to move the slow job out of the request: queue it and return `202` with a status URL (swe.08 section 8), and keep `timeout` just above your slowest *interactive* request.

</details>

## 3. Configuration from the environment

### 3.1 The rule

**Configuration is everything that changes between deployments** (database address, secrets, log level, which payment provider, feature flags). **Code does not change between deployments.** Keep the two apart. A quick test: *could you publish your repository today without leaking a credential or breaking a production setting?* If not, there is configuration in your code.

### 3.2 Where settings come from, and who wins

| Source | Example | When |
|---|---|---|
| **Defaults in code** | `log_level = "INFO"` | safe, harmless values for development |
| **Image defaults** (`ENV` in a Dockerfile) | `ENV DATABASE_PATH=/data/pagebound.db` | paths and values that are part of how the image is built |
| **Environment variables** | `APP_ENV=production` | the normal way to configure a deployment |
| **Files** | `.env`, mounted config or secret files | local development; secrets mounted as files |
| **Command-line flags** | `--workers 4` | overrides for one run |

Later sources win. Whatever the sources, load them **once, at start-up, into a validated object** and **refuse to start** when it is wrong. A service that boots with a missing or invalid setting fails at 3 a.m. under load instead of at deploy time.

### 3.3 A Settings class that fails fast

This is the configuration module of the service we will operate. It reads the environment once, checks it, and hides the secret when printed:

```python
# app/config.py
"""Configuration comes from the environment (twelve-factor). One place reads it; everything else receives a Settings object."""
import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    version: str = "dev"
    database_path: str = "pagebound.db"
    redis_url: str | None = None
    log_level: str = "INFO"
    secret_key: str = ""

    @classmethod
    def from_env(cls, environ=None) -> "Settings":
        e = os.environ if environ is None else environ
        settings = cls(
            env=e.get("APP_ENV", "development"),
            version=e.get("APP_VERSION", "dev"),
            database_path=e.get("DATABASE_PATH", "pagebound.db"),
            redis_url=e.get("REDIS_URL") or None,
            log_level=e.get("LOG_LEVEL", "INFO").upper(),
            secret_key=e.get("APP_SECRET_KEY", ""),
        )
        problems = []
        if settings.env not in {"development", "test", "production"}:
            problems.append(f"APP_ENV must be development, test or production (got {settings.env!r})")
        if settings.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            problems.append(f"LOG_LEVEL is not a valid level: {settings.log_level!r}")
        if settings.env == "production" and len(settings.secret_key) < 32:
            problems.append("APP_SECRET_KEY must be set to at least 32 characters in production")
        if problems:
            raise ConfigError("; ".join(problems))                  # refuse to start with a bad configuration
        return settings

    def __repr__(self) -> str:                                       # never print the secret
        return (f"Settings(env={self.env!r}, version={self.version!r}, database_path={self.database_path!r}, "
                f"redis_url={'set' if self.redis_url else None}, log_level={self.log_level!r}, secret_key='***')")
```

```python run
from app.config import ConfigError, Settings

print(Settings.from_env({}))                                       # defaults for development
print(Settings.from_env({"APP_ENV": "production", "APP_SECRET_KEY": "k" * 40, "REDIS_URL": "redis://redis:6379/0", "APP_VERSION": "1.4.2"}))
for bad in ({"APP_ENV": "production"}, {"APP_ENV": "prod"}, {"LOG_LEVEL": "LOUD"}):
    try:
        Settings.from_env(bad)
    except ConfigError as exc:
        print("refused to start:", exc)
```
```text
Settings(env='development', version='dev', database_path='pagebound.db', redis_url=None, log_level='INFO', secret_key='***')
Settings(env='production', version='1.4.2', database_path='pagebound.db', redis_url=set, log_level='INFO', secret_key='***')
refused to start: APP_SECRET_KEY must be set to at least 32 characters in production
refused to start: APP_ENV must be development, test or production (got 'prod')
refused to start: LOG_LEVEL is not a valid level: 'LOUD'
```

All the problems are reported together (not one at a time), the secret key never appears in `repr`, and the production rule (a long secret) is enforced by the code rather than by someone's memory.

### 3.4 How Docker passes settings in

The same tiny test works with any container. The Python image gives us a throw-away process to print what it receives:

```bash run
docker run --rm -e APP_ENV=production -e LOG_LEVEL=WARNING python:3.14-slim python -c "import os; print(os.environ['APP_ENV'], os.environ['LOG_LEVEL'])"
printf 'APP_ENV=staging\nLOG_LEVEL=DEBUG\n' > demo.env
docker run --rm --env-file demo.env python:3.14-slim python -c "import os; print(os.environ['APP_ENV'], os.environ['LOG_LEVEL'])"
docker run --rm --env-file demo.env -e LOG_LEVEL=ERROR python:3.14-slim python -c "import os; print(os.environ['APP_ENV'], os.environ['LOG_LEVEL'])"
```
```text
production WARNING
staging DEBUG
staging ERROR
```

`-e NAME=value` sets one variable, `--env-file` loads many from a file (`NAME=value` lines, no quotes needed), and an explicit `-e` wins over the file. In Docker Compose there are two similar-looking features that people mix up (section 6): a file called `.env` next to `compose.yaml` is used to **substitute `${VARIABLES}` inside the compose file itself**, while `env_file:` or `environment:` on a service sets variables **inside the container**.

### 3.5 `.env` files and secrets

- A `.env` file is for **local convenience**. Add `.env` to `.gitignore` and `.dockerignore`, and commit a `.env.example` with the variable names and fake values so that others know what to set.
- **Never bake secrets into an image** (`ENV SECRET=...` or `COPY .env`). Anyone who can pull the image can read it with `docker history` or by unpacking the layers.
- **Never pass secrets as command-line arguments.** The command line of every process is readable by every user on the machine:

```bash run
python3 -c "import time; time.sleep(5)" --api-token=s3cr3t-token-123 &
pid=$!
sleep 0.5
echo "anyone on the machine can run:  ps -p <pid> -o args"
ps -p "$pid" -o args=
kill "$pid"
```
```text
anyone on the machine can run:  ps -p <pid> -o args
python3 -c import time; time.sleep(5) --api-token=s3cr3t-token-123
```

- In production, secrets come from a **secret manager** (AWS Secrets Manager, Google Secret Manager, HashiCorp Vault) or from the platform's secret store (Docker/Kubernetes secrets), delivered as environment variables or as **mounted files**. The `FOO_FILE=/run/secrets/foo` convention (the app reads the secret from the file the variable names) keeps values out of `docker inspect`.
- **Rotate** secrets on a schedule and after any leak, and keep a different value in every environment.

### 3.6 Feature flags and drift

A **feature flag** is a setting that turns behaviour on or off without a deployment (`NEW_CHECKOUT=1`). Flags let you deploy code that is not yet switched on (safer releases, section 12) and switch a misbehaving feature off in seconds. Remove old flags, since each one doubles the paths to test. **Configuration drift** is when production and staging slowly differ in hidden ways (someone edited a setting by hand): keep configuration in files under version control or in your secret manager's history, and have the application print its non-secret settings at start-up (as the `starting` log line does in section 5).

### Try it: spot the leak

Which of these puts a secret at risk? (a) `ENV STRIPE_KEY=sk_live_...` in the Dockerfile; (b) `docker run -e STRIPE_KEY=...` typed in a shared shell with history; (c) `STRIPE_KEY` in `.env`, with `.env` in `.gitignore` and `.dockerignore`; (d) `python app.py --stripe-key sk_live_...` in a systemd unit.

<details><summary>Answer</summary>

(a) Yes: the key becomes part of the image and its history for everyone who can pull it. (b) A mild risk: it lands in shell history and in `docker inspect` output; better is `--env-file` from a file with restricted permissions, or a secret store. (c) Fine for local development. (d) Yes: the command line is visible to every user via `ps`, and unit files are often world-readable. Use `EnvironmentFile=` with mode 600 or a secret manager.

</details>

### Try it: fail fast

The service reads `os.environ.get("DATABASE_URL", "sqlite:///dev.db")` deep inside a function called on the first request. In production someone forgets to set `DATABASE_URL`. What happens, and what is the better design?

<details><summary>Answer</summary>

The app starts and passes its health checks, then silently uses a local development SQLite file inside the container: data written there disappears with the container, and the bug is found by users. Better: read all settings once at start-up in a `Settings` object, make dangerous settings **required in production** (no default), and refuse to start with a clear message, so the deployment fails (and rolls back) before any traffic arrives.

</details>


## 4. Docker, step by step

### 4.1 What problem Docker solves

"It works on my machine" usually means "it works with *my* Python version, *my* libraries, *my* environment variables, *my* operating system packages". A deployment target has different ones. **Docker** packages an application together with everything it needs to run (the Python interpreter, the libraries, the system files) into one **image**. Anyone can run that image anywhere Docker runs, and gets the same result.

Three words you must keep apart:

| Word | What it is | Analogy |
|---|---|---|
| **Image** | a read-only package: filesystem layers plus defaults (command, environment) | a recipe, or a class |
| **Container** | a running (or stopped) instance of an image, with its own process, filesystem changes and network | a dish made from the recipe, or an object |
| **Registry** | a server that stores images (Docker Hub, GitHub Container Registry, a cloud registry) | an app store |

A container is **not a virtual machine**. It is an ordinary process on your computer's kernel, wrapped in isolation: its own view of the filesystem, process list and network (Linux *namespaces*) and limits on memory and CPU (*cgroups*). That is why containers start in a fraction of a second and are small, and also why they are **not a security boundary as strong as a VM**.

An image is built from **layers**. Each Dockerfile instruction adds a layer; layers are stored once and shared (two images built on `python:3.14-slim` share its layers), and Docker caches them so a rebuild only redoes what changed. Section 5 shows this working.

### 4.2 Tutorial A: your first containers

Every command here runs a throw-away container (`--rm` removes it when it exits).

```bash run
docker run --rm hello-world | sed -n '2,3p'
docker run --rm python:3.14-slim python -c "import sys, platform; print('python', sys.version.split()[0], 'on', platform.system(), platform.machine())"
docker run --rm python:3.14-slim cat /etc/os-release | head -2
```
```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
python 3.14.10 on Linux x86_64
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
```

The second command did four things: found the image `python:3.14-slim` locally (or pulled it from Docker Hub the first time), created a container, ran `python -c ...` inside it, and removed it. The third shows that the container has its **own filesystem** (a Debian system), whatever your host runs. The image name has the form `repository:tag`; the tag `3.14-slim` means "Python 3.14, the small Debian variant". Tags are movable labels: `python:3.14-slim` will point to newer patch releases over time, which is why production images pin a specific version (section 5.6).

### 4.3 Tutorial B: a long-running container

`-d` runs the container in the background ("detached"), `--name` gives it a name, `-p` publishes a port. `-p 127.0.0.1:18010:8000` means "connections to port 18010 on **this machine only** go to port 8000 inside the container". (Without `127.0.0.1:` Docker publishes on all interfaces, which can expose a development service to your whole network, and Docker bypasses simple `ufw` rules when it does. Be explicit.)

```bash run
docker run -d --name pbtut-web -p 127.0.0.1:18010:8000 python:3.14-slim python -m http.server 8000
sleep 2
curl -s localhost:18010 | head -4
echo "--- status"
docker ps --filter name=pbtut-web --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | sed -E 's/Up [0-9]+ seconds?/Up N seconds/'
echo "--- logs (what the process wrote to stdout/stderr)"
docker logs pbtut-web 2>&1 | head -2
echo "--- run a command inside the running container"
docker exec pbtut-web python -c "import os; print('pid 1 is', open('/proc/1/cmdline').read().replace(chr(0), ' ').strip())"
echo "--- inspect: ask Docker for facts about it"
docker inspect --format 'status={{.State.Status}} image={{.Config.Image}} restart={{.HostConfig.RestartPolicy.Name}}' pbtut-web
```
```text
b3e8aa3dcdc10b95aebc32e75196fce213b3944a096054db4d9f9482e3fc1a28
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
--- status
NAMES       IMAGE              STATUS         PORTS
pbtut-web   python:3.14-slim   Up N seconds   127.0.0.1:18010->8000/tcp
--- logs (what the process wrote to stdout/stderr)
172.17.0.1 - - [09/Nov/2026 07:44:49] "GET / HTTP/1.1" 200 -
--- run a command inside the running container
pid 1 is python -m http.server 8000
--- inspect: ask Docker for facts about it
status=running image=python:3.14-slim restart=no
```

`docker logs` shows everything the container's main process wrote to **standard output and standard error**. That is why containerised apps log to stdout (section 8) and do not manage log files: Docker (and later your platform) collects the stream. `docker exec` starts an *additional* process inside the container: your tool for looking around. `docker inspect` prints everything Docker knows as JSON; `--format` picks fields.

**Stopping**, and the most important surprise for newcomers. `docker stop` sends `SIGTERM` to the container's main process (PID 1), waits for a grace period, and then sends `SIGKILL`. A process running as PID 1 gets *special* treatment from Linux: signals without an installed handler are ignored. Plain Python does not install a `SIGTERM` handler, so it ignores the request:

```bash run
now() { python3 -c "import time; print(time.time())"; }
start=$(now)
docker stop -t 3 pbtut-web > /dev/null
end=$(now)
python3 -c "print('plain python as PID 1 ignored SIGTERM; docker waited out the 3 s grace period and then killed it:', $end - $start >= 3.0)"
docker rm pbtut-web > /dev/null

docker run -d --init --name pbtut-web -p 127.0.0.1:18010:8000 python:3.14-slim python -m http.server 8000 > /dev/null
sleep 1
start=$(now)
docker stop -t 3 pbtut-web > /dev/null
end=$(now)
python3 -c "print('with --init (a tiny init process forwards signals) it stopped at once:', $end - $start < 1.0)"
docker rm pbtut-web > /dev/null
```
```text
plain python as PID 1 ignored SIGTERM; docker waited out the 3 s grace period and then killed it: True
with --init (a tiny init process forwards signals) it stopped at once: True
```

The lesson: **a service that does not handle `SIGTERM` is killed rudely after the grace period** (10 seconds by default), which in a deployment means dropped requests and half-finished work (swe.08 section 10.2). Servers such as Uvicorn and Gunicorn handle `SIGTERM` correctly; your own scripts need a handler, or `docker run --init` / `init: true` in Compose.

### 4.4 Tutorial C: data, volumes and bind mounts

A container's filesystem changes disappear with the container. Data that must survive lives in a **volume** (managed by Docker) or a **bind mount** (a folder from your computer):

```bash run
echo "--- without a volume: the file dies with the container"
docker run --rm python:3.14-slim sh -c 'echo important > /data.txt; cat /data.txt'
docker run --rm python:3.14-slim sh -c 'cat /data.txt 2>&1 || true' | sed 's/^/second container: /'

echo "--- with a named volume: it survives"
docker volume create pbtut-demo > /dev/null
docker run --rm -v pbtut-demo:/data python:3.14-slim sh -c 'echo important > /data/note.txt'
docker run --rm -v pbtut-demo:/data python:3.14-slim cat /data/note.txt | sed 's/^/second container: /'

echo "--- a bind mount shows a folder of the host, read-only here (:ro)"
mkdir -p site && echo "<h1>hello from the host</h1>" > site/index.html
docker run --rm -v "$PWD/site:/site:ro" python:3.14-slim sh -c 'cat /site/index.html; touch /site/new 2>&1 | head -1'
docker volume rm pbtut-demo > /dev/null
```
```text
--- without a volume: the file dies with the container
important
second container: cat: /data.txt: No such file or directory
--- with a named volume: it survives
second container: important
--- a bind mount shows a folder of the host, read-only here (:ro)
<h1>hello from the host</h1>
touch: cannot touch '/site/new': Read-only file system
```

| Kind | Syntax | Use |
|---|---|---|
| **Named volume** | `-v name:/path` | databases, uploads: data Docker manages and you back up (section 13) |
| **Bind mount** | `-v /host/path:/path` | development (live code), configuration files (`:ro`) |
| **tmpfs** | `--tmpfs /tmp` | scratch space that never touches disk |

### 4.5 Tutorial D: networks and names

Containers on a **user-defined network** can reach each other **by name**. The default network does not provide that:

```bash run
docker network create pbtut-net > /dev/null
docker run -d --name pbtut-a --network pbtut-net python:3.14-slim python -m http.server 8000 > /dev/null
sleep 1
echo "same network, by name:"
docker run --rm --network pbtut-net python:3.14-slim python -c "import urllib.request as u; print('  status', u.urlopen('http://pbtut-a:8000').status)"
echo "default network, by name:"
docker run --rm python:3.14-slim python -c "import urllib.request as u; u.urlopen('http://pbtut-a:8000', timeout=2)" 2>&1 | tail -1 | sed 's/^/  /'
docker rm -f pbtut-a > /dev/null
docker network rm pbtut-net > /dev/null
```
```text
same network, by name:
  status 200
default network, by name:
  urllib.error.URLError: <urlopen error [Errno -2] Name or service not known>
```

This is how an application finds its database in Compose: the service name **is** the host name (`redis://redis:6379`). Remember also that **`localhost` inside a container means the container itself**, not your computer: a classic cause of "connection refused" when an app in a container tries to reach a database running on the host.

### 4.6 Tutorial E: limits and restart policies

A container may use all the memory and CPU of the machine unless you set limits. When it exceeds its memory limit, the kernel's out-of-memory killer ends it (exit code **137** = 128 + 9, `SIGKILL`):

```bash run
docker run --name pbtut-oom --memory 64m --memory-swap 64m python:3.14-slim python -c "x = bytearray(300_000_000); print('allocated')"
echo "exit code: $?"
docker inspect --format 'OOMKilled={{.State.OOMKilled}} ExitCode={{.State.ExitCode}}' pbtut-oom
docker rm pbtut-oom > /dev/null
```
```text
exit code: 137
OOMKilled=true ExitCode=137
```

A **restart policy** says what Docker does when a container exits: `no` (default), `on-failure[:N]`, `always`, `unless-stopped`. A container that exits with an error is restarted; one that you stopped by hand stays stopped:

```bash run
docker run -d --name pbtut-flaky --restart on-failure:3 python:3.14-slim python -c "import sys; print('crashing'); sys.exit(3)" > /dev/null
sleep 8
docker inspect --format 'restarts={{.RestartCount}} status={{.State.Status}} exit={{.State.ExitCode}}' pbtut-flaky
docker logs pbtut-flaky 2>&1 | sort | uniq -c
docker rm -f pbtut-flaky > /dev/null
```
```text
restarts=3 status=exited exit=3
      4 crashing
```

It crashed, was restarted three times (with growing pauses) and then Docker gave up. A **crash loop** like this is the signal that something is broken, not something to hide: alert on restart counts (section 10).

### 4.7 Cheat sheet

| Task | Command |
|---|---|
| list running / all containers | `docker ps` / `docker ps -a` |
| run a container | `docker run [-d] [--rm] [--name N] [-p H:C] [-e K=V] [-v SRC:DST] IMAGE [COMMAND]` |
| logs, follow | `docker logs [-f] [--tail N] NAME` |
| shell inside | `docker exec -it NAME sh` |
| stop / force / remove | `docker stop NAME` / `docker kill NAME` / `docker rm [-f] NAME` |
| images | `docker images`, `docker pull IMAGE`, `docker rmi IMAGE` |
| facts as JSON | `docker inspect NAME` |
| copy files | `docker cp NAME:/path ./here` and `docker cp ./file NAME:/path` |
| resource use | `docker stats --no-stream` |
| disk used by Docker | `docker system df` |
| build an image | `docker build -t name:tag .` |

Safe cleanup for **this chapter only**: `docker ps -a --filter name=^pbtut` shows what is ours; `docker rm -f $(docker ps -aq --filter name=^pbtut)` removes exactly those. Reserve `docker system prune` for machines where you know that nothing else matters.

### Try it: predict

You run `docker run -d --name web -p 8000:8000 myapp` on a laptop on café Wi-Fi. Who can reach the app? How do you change it, and what happens to your data if you then run `docker rm -f web`?

<details><summary>Answer</summary>

Without an address in `-p`, Docker publishes the port on **all interfaces**, so anyone on the same network can reach it. Use `-p 127.0.0.1:8000:8000` for local-only access. Any data written inside the container's own filesystem is destroyed by `docker rm`; only volumes (or bind mounts) survive.

</details>

### Try it: exit code 137

A container "dies for no reason" with exit code 137, but `docker logs` shows nothing wrong. Name two causes and how to tell them apart.

<details><summary>Answer</summary>

137 is `SIGKILL`. Either the **out-of-memory killer** ended it (`docker inspect` shows `OOMKilled=true`; the fix is less memory use or a higher limit), or something sent `SIGKILL`: `docker kill`, a `docker stop` whose grace period ran out because the process ignored `SIGTERM` (section 4.3), or the host's orchestrator. Check `OOMKilled`, then the times of the stop request and the exit.

</details>

## 5. Dockerising the Pagebound service

### 5.1 The service we will operate

From here to the end, one small FastAPI service called **Pagebound** is the patient. It is built the way an operable service should be: configuration from the environment (section 3, already written), JSON logs with a request id, liveness and readiness endpoints, metrics, graceful shutdown. Here is the code. Sections 8, 9 and 10 explain the logging, health and metrics parts in depth; for now read it once to see what it does.

The logging module: every log line is one JSON object, and the **request id** is carried in a context variable so that any code, anywhere, can log it without passing it around:

```python
# app/logs.py
"""JSON logs on stdout, with the request id attached to every line."""
import contextvars
import json
import logging
import sys
import time

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        entry.update(getattr(record, "fields", {}))                  # structured extras: log.info("x", extra={"fields": {...}})
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, separators=(",", ":"))


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    logging.getLogger("uvicorn.access").disabled = True              # the app writes its own access line
```

The metrics module: a small registry that renders the text format Prometheus reads:

```python
# app/metrics.py
"""A tiny metrics registry that renders the Prometheus text format (requests counter, latency histogram)."""
import threading
from collections import defaultdict

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.requests = defaultdict(int)                             # (method, route, status) -> count
        self.bucket_counts = defaultdict(lambda: [0] * len(BUCKETS))
        self.sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.in_flight = 0

    def observe(self, method: str, route: str, status: int, seconds: float) -> None:
        with self._lock:
            self.requests[(method, route, str(status))] += 1
            key = (method, route)
            self.sums[key] += seconds
            self.counts[key] += 1
            for i, upper in enumerate(BUCKETS):
                if seconds <= upper:
                    self.bucket_counts[key][i] += 1

    def render(self) -> str:
        lines = ["# HELP http_requests_total Requests handled, by method, route template and status.",
                 "# TYPE http_requests_total counter"]
        for (method, route, status), n in sorted(self.requests.items()):
            lines.append(f'http_requests_total{{method="{method}",route="{route}",status="{status}"}} {n}')
        lines += ["# HELP http_request_duration_seconds Request latency.", "# TYPE http_request_duration_seconds histogram"]
        for (method, route), counts in sorted(self.bucket_counts.items()):
            labels = f'method="{method}",route="{route}"'
            for upper, n in zip(BUCKETS, counts):
                lines.append(f'http_request_duration_seconds_bucket{{{labels},le="{upper}"}} {n}')
            lines.append(f'http_request_duration_seconds_bucket{{{labels},le="+Inf"}} {self.counts[(method, route)]}')
            lines.append(f'http_request_duration_seconds_sum{{{labels}}} {self.sums[(method, route)]:.6f}')
            lines.append(f'http_request_duration_seconds_count{{{labels}}} {self.counts[(method, route)]}')
        lines += ["# HELP http_requests_in_flight Requests being handled right now.", "# TYPE http_requests_in_flight gauge",
                  f"http_requests_in_flight {self.in_flight}"]
        return "\n".join(lines) + "\n"
```

The application itself. Note the `RequestContext` middleware (request id in and out, one access-log line, metrics), the `lifespan` function (start-up and graceful shutdown), and the endpoints, among them `/healthz`, `/readyz`, `/metrics`, and deliberately a `/boom` endpoint that fails, for the exercises:

```python
# app/main.py
import asyncio
import logging
import os
import re
import socket
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager, closing

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from .config import Settings
from .logs import configure_logging, request_id_var
from .metrics import Metrics

log = logging.getLogger("pagebound")
VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
QUIET_PATHS = {"/healthz", "/readyz", "/metrics"}


class RequestContext:
    """Pure ASGI middleware: request id in, request id out, one access-log line, metrics."""

    def __init__(self, app, metrics: Metrics):
        self.app, self.metrics = app, metrics

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex          # never trust a client-supplied id blindly
        token = request_id_var.set(rid)
        started, status = time.perf_counter(), 500
        self.metrics.in_flight += 1

        async def send_with_id(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            log.exception("unhandled error")                                      # full traceback goes to the log...
            response = JSONResponse({"error": "internal error", "request_id": rid}, status_code=500)   # ...the client only gets the id
            await response(scope, receive, send_with_id)
        finally:
            seconds = time.perf_counter() - started
            route = getattr(scope.get("route"), "path", "unmatched")
            self.metrics.in_flight -= 1
            self.metrics.observe(scope["method"], route, status, seconds)
            client = scope.get("client") or ("-", 0)
            if scope["path"] not in QUIET_PATHS:                                     # do not log health probes and scrapes
                log.info("request", extra={"fields": {"method": scope["method"], "path": scope["path"], "route": route,
                                                      "status": status, "duration_ms": round(seconds * 1000, 1), "client": client[0]}})
            request_id_var.reset(token)


class OrderIn(BaseModel):
    item: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=1000)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)
    metrics = Metrics()
    instance = socket.gethostname()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with closing(sqlite3.connect(settings.database_path)) as db:
            db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL)")
            db.commit()
        log.info("starting", extra={"fields": {"version": settings.version, "env": settings.env, "instance": instance}})
        yield
        app.state.draining = True                                                  # readiness goes red before we exit
        log.info("shutting down")

    app = FastAPI(title="Pagebound API", version=settings.version, lifespan=lifespan, docs_url=None if settings.env == "production" else "/docs")
    app.state.draining = False
    app.state.hits = 0
    app.add_middleware(RequestContext, metrics=metrics)

    def redis_client():
        import redis                                                               # imported lazily: optional dependency
        return redis.Redis.from_url(settings.redis_url, socket_timeout=1, decode_responses=True)

    @app.get("/")
    def index():
        return {"service": "pagebound", "version": settings.version, "env": settings.env, "instance": instance}

    @app.get("/whoami")
    def whoami():
        return {"instance": instance, "pid": os.getpid()}

    @app.post("/orders", status_code=201)
    def create_order(body: OrderIn):
        with closing(sqlite3.connect(settings.database_path)) as db:
            cur = db.execute("INSERT INTO orders (item, quantity) VALUES (?, ?)", (body.item, body.quantity))
            db.commit()
        log.info("order created", extra={"fields": {"order_id": cur.lastrowid, "item": body.item}})
        return {"id": cur.lastrowid, **body.model_dump()}

    @app.get("/orders/{order_id}")
    def get_order(order_id: int):
        with closing(sqlite3.connect(settings.database_path)) as db:
            row = db.execute("SELECT id, item, quantity FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "order not found")
        return {"id": row[0], "item": row[1], "quantity": row[2]}

    @app.get("/hits")
    def hits():
        if settings.redis_url:
            return {"hits": redis_client().incr("pagebound:hits"), "store": "redis", "instance": instance}
        app.state.hits += 1
        return {"hits": app.state.hits, "store": "memory", "instance": instance}

    @app.get("/slow")
    async def slow(seconds: float = 0.2):
        await asyncio.sleep(min(seconds, 30))
        return {"slept": seconds}

    @app.get("/boom")
    def boom():
        raise RuntimeError("simulated bug while building the invoice")

    @app.get("/healthz")
    def healthz():
        return {"status": "alive"}                                                 # liveness: the process runs; checks NOTHING else

    @app.get("/readyz")
    def readyz():
        problems = {}
        if app.state.draining:
            problems["draining"] = "shutting down"
        try:
            with closing(sqlite3.connect(settings.database_path, timeout=1)) as db:
                db.execute("SELECT 1").fetchone()
        except sqlite3.Error as exc:
            problems["database"] = str(exc)
        if settings.redis_url:
            try:
                redis_client().ping()
            except Exception as exc:
                problems["redis"] = type(exc).__name__
        if problems:
            return JSONResponse({"status": "not ready", "problems": problems}, status_code=503)
        return {"status": "ready"}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics_endpoint():
        return metrics.render()

    return app
```

```text
requirements.txt           pinned dependencies (exact versions, so every build is repeatable)
app/config.py, logs.py, metrics.py, main.py
tests/test_app.py          tests that run without Docker
```

```text
# requirements.txt
fastapi==0.162.0
uvicorn==0.54.0
pydantic==2.14.3
redis==6.4.0
```

The tests run on the host with plain `pytest`, no Docker involved. Run them before every build; an image containing broken code is still broken, only now it is also big.

```python
# tests/test_app.py
import logging
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.config import ConfigError, Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    settings = Settings(database_path=str(tmp_path / "t.db"))
    with TestClient(create_app(settings), raise_server_exceptions=False) as c:
        yield c


def test_request_id_is_echoed_and_generated(client):
    assert client.get("/", headers={"X-Request-ID": "trace-me-0001"}).headers["x-request-id"] == "trace-me-0001"
    generated = client.get("/").headers["x-request-id"]
    assert len(generated) == 32
    unsafe = client.get("/", headers={"X-Request-ID": "bad id with spaces\n"}).headers["x-request-id"]
    assert unsafe != "bad id with spaces", "a malformed client id must be replaced"


def test_unhandled_error_gives_the_client_only_the_request_id(client, caplog):
    with caplog.at_level(logging.ERROR):
        r = client.get("/boom", headers={"X-Request-ID": "trace-me-0002"})
    assert r.status_code == 500
    assert r.json() == {"error": "internal error", "request_id": "trace-me-0002"}
    assert "simulated bug" not in r.text, "internal details must not reach the client"
    assert "simulated bug" in caplog.text, "...but they must be in the log"


def test_orders_round_trip_and_validation(client):
    created = client.post("/orders", json={"item": "pen", "quantity": 3})
    assert created.status_code == 201
    assert client.get(f"/orders/{created.json()['id']}").json()["item"] == "pen"
    assert client.get("/orders/999").status_code == 404
    assert client.post("/orders", json={"item": "pen", "quantity": 0}).status_code == 422


def test_health_and_readiness(client, monkeypatch):
    assert client.get("/healthz").json() == {"status": "alive"}
    assert client.get("/readyz").json() == {"status": "ready"}

    def broken(*args, **kwargs):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr("app.main.sqlite3.connect", broken)
    not_ready = client.get("/readyz")
    assert not_ready.status_code == 503 and "database" in not_ready.json()["problems"]
    assert client.get("/healthz").status_code == 200, "liveness must NOT depend on the database"
    monkeypatch.undo()
    client.app.state.draining = True
    assert client.get("/readyz").status_code == 503, "a draining instance must report not-ready"


def test_metrics_use_route_templates_not_raw_paths(client):
    client.get("/orders/1")
    client.get("/orders/2")
    text = client.get("/metrics").text
    assert 'route="/orders/{order_id}"' in text and "/orders/1" not in text, "raw paths would explode the label cardinality"
    assert 'http_requests_total{method="GET",route="/orders/{order_id}",status="404"} 2' in text


def test_configuration_fails_fast():
    assert Settings.from_env({}).env == "development"
    with pytest.raises(ConfigError, match="APP_SECRET_KEY"):
        Settings.from_env({"APP_ENV": "production"})
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        Settings.from_env({"LOG_LEVEL": "LOUD"})
    assert "s" * 40 not in repr(Settings.from_env({"APP_SECRET_KEY": "s" * 40})), "the secret must never be printed"
```

```bash run
python -m pytest -q -p no:cacheprovider -W ignore tests 2>&1 | tail -3
```
```text
......                                                                   [100%]
6 passed in 0.29s
```

### 5.2 The Dockerfile

A **Dockerfile** is the recipe for an image. Here is the one for Pagebound. Read the comments, then the table.

```dockerfile
# Dockerfile
# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN useradd --create-home --uid 10001 app
WORKDIR /srv

# dependencies first: this layer is rebuilt only when requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# application code last: it changes most often
COPY app ./app

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    DATABASE_PATH=/data/pagebound.db
RUN mkdir /data && chown app:app /data
VOLUME /data

USER app
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=1).status == 200 else 1)"]

# exec form: uvicorn is PID 1 and receives SIGTERM directly
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
```

| Instruction | What it does, and why it is placed here |
|---|---|
| `FROM python:3.14-slim` | the base image; `slim` is Debian without build tools (much smaller than the full image) |
| `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ...` | no `.pyc` files; **unbuffered output**, so log lines appear immediately in `docker logs`; pip without cache or version nagging |
| `RUN useradd ... app` | creates an unprivileged user (used by `USER app` below) |
| `WORKDIR /srv` | the working directory for later instructions and the running app |
| `COPY requirements.txt .` then `RUN pip install` | **dependencies first**: this layer is rebuilt only when `requirements.txt` changes |
| `COPY app ./app` | **code last**: it changes with almost every commit, so it must come after the slow layers |
| `ARG APP_VERSION` / `ENV APP_VERSION` | a build-time value stored as a runtime default, so the service can report which version it is |
| `RUN mkdir /data && chown ...`, `VOLUME /data` | the folder for the database, writable by the unprivileged user, declared as a volume |
| `USER app` | the process does **not** run as root; a bug or exploit in the app does not get root inside the container |
| `HEALTHCHECK` | Docker runs this command regularly; "healthy" or "unhealthy" shows in `docker ps` (section 9) |
| `CMD ["uvicorn", ...]` | the command to run, in **exec form** (a JSON list), so Uvicorn is PID 1 and receives `SIGTERM` itself |

A `.dockerignore` file keeps files out of the **build context** (everything Docker sends to the build). It speeds builds and, more importantly, prevents secrets and junk from landing in the image:

```text
# .dockerignore
.git
.venv
__pycache__
*.pyc
.pytest_cache
.env
*.db
tests
out
backups
```

### 5.3 Build it, and understand the cache

```bash run
docker build --progress=plain --no-cache -t pagebound-api:1.0.0 --build-arg APP_VERSION=1.0.0 . 2>&1 | tail -n 4 | sed -E 's/[0-9.]+s$//; s/sha256:[0-9a-f]{12,}/sha256:.../'
docker images pagebound-api:1.0.0 --format 'image {{.Repository}}:{{.Tag}}  size {{.Size}}'
```
```text
#14 naming to docker.io/library/pagebound-api:1.0.0 done
#14 unpacking to docker.io/library/pagebound-api:1.0.0
#14 unpacking to docker.io/library/pagebound-api:1.0.0 0.2s done
#14 DONE 
image pagebound-api:1.0.0  size 208MB
```

(The first build downloads the packages and takes some time; `--no-cache` forces every step to run so that the demonstration below starts from a known state. The image size depends on the base image version.) Now change **only the application code** and build again, then change **only the dependencies**, and watch which steps Docker has to redo. A small script turns the build log into a table:

```bash run
cat > buildsteps.py <<'PYEOF'
import re, sys
log = sys.stdin.read()
steps = {m.group(1): (m.group(2), re.sub(r"@sha256:[0-9a-f]+", "", m.group(3))) for m in re.finditer(r"^#(\d+) \[(\d+/\d+)\] (.+)$", log, re.M)}
cached = set(re.findall(r"^#(\d+) CACHED", log, re.M))
for number, (position, what) in sorted(steps.items(), key=lambda item: int(item[1][0].split("/")[0])):
    print(f"{'CACHED' if number in cached else 'REBUILT':8}{position:6}{what[:62]}")
PYEOF

echo "--- 1. nothing changed"
docker build --progress=plain -t pagebound-api:1.0.0 --build-arg APP_VERSION=1.0.0 . 2>&1 | python buildsteps.py

echo "--- 2. one line of application code changed"
echo "# touched" >> app/config.py
docker build --progress=plain -t pagebound-api:1.0.0 --build-arg APP_VERSION=1.0.0 . 2>&1 | python buildsteps.py

echo "--- 3. a dependency changed (this reinstalls everything)"
cp requirements.txt requirements.bak
echo "# a comment is enough to change the file" >> requirements.txt
docker build --progress=plain -t pagebound-api:1.0.0 --build-arg APP_VERSION=1.0.0 . 2>&1 | python buildsteps.py
mv requirements.bak requirements.txt
sed -i '$ d' app/config.py
```
```text
--- 1. nothing changed
REBUILT 1/7   FROM docker.io/library/python:3.14-slim
CACHED  2/7   RUN useradd --create-home --uid 10001 app
CACHED  3/7   WORKDIR /srv
CACHED  4/7   COPY requirements.txt .
CACHED  5/7   RUN pip install -r requirements.txt
CACHED  6/7   COPY app ./app
CACHED  7/7   RUN mkdir /data && chown app:app /data
--- 2. one line of application code changed
REBUILT 1/7   FROM docker.io/library/python:3.14-slim
CACHED  2/7   RUN useradd --create-home --uid 10001 app
CACHED  3/7   WORKDIR /srv
CACHED  4/7   COPY requirements.txt .
CACHED  5/7   RUN pip install -r requirements.txt
CACHED  6/7   COPY app ./app
CACHED  7/7   RUN mkdir /data && chown app:app /data
--- 3. a dependency changed (this reinstalls everything)
REBUILT 1/7   FROM docker.io/library/python:3.14-slim
CACHED  2/7   RUN useradd --create-home --uid 10001 app
CACHED  3/7   WORKDIR /srv
CACHED  4/7   COPY requirements.txt .
CACHED  5/7   RUN pip install -r requirements.txt
CACHED  6/7   COPY app ./app
CACHED  7/7   RUN mkdir /data && chown app:app /data
```

In case 2 the expensive `pip install` step is **CACHED** because `requirements.txt` did not change, and only the copy of the application code is rebuilt (a second or two). In case 3 the `COPY requirements.txt` layer changes, and every layer **after** it is invalid, including the install. That is the reason for the order in the Dockerfile: **things that change rarely come first.** If you wrote `COPY . .` before `pip install`, every code change would reinstall every dependency.

### 5.4 Run it

```bash run
docker run -d --name pbtut-api -p 127.0.0.1:18020:8000 -e APP_ENV=development pagebound-api:1.0.0 > /dev/null
echo "health right after start: $(docker inspect --format '{{.State.Health.Status}}' pbtut-api)"
for i in $(seq 1 20); do
  [ "$(docker inspect --format '{{.State.Health.Status}}' pbtut-api)" = healthy ] && break
  sleep 1
done
echo "health after a few seconds: $(docker inspect --format '{{.State.Health.Status}}' pbtut-api)"
curl -s localhost:18020/ | jq -c 'del(.instance)'
curl -s -X POST localhost:18020/orders -H 'content-type: application/json' -d '{"item": "pen", "quantity": 3}'; echo
curl -s localhost:18020/orders/1; echo
echo "--- the container runs as:"
docker exec pbtut-api id -un
echo "--- the first log lines (JSON, one object per line):"
docker logs pbtut-api 2>&1 | grep '^{' | head -2 | jq -c 'del(.ts, .instance)'
echo "--- the largest layers:"
docker history --format '{{.Size}}\t{{.CreatedBy}}' pagebound-api:1.0.0 | grep -v "^0B" | head -4 | cut -c1-90
```
```text
health right after start: starting
health after a few seconds: healthy
{"service":"pagebound","version":"1.0.0","env":"development"}
{"id":1,"item":"pen","quantity":3}
{"id":1,"item":"pen","quantity":3}
--- the container runs as:
app
--- the first log lines (JSON, one object per line):
{"level":"INFO","logger":"pagebound","msg":"starting","request_id":"-","version":"1.0.0","env":"development"}
{"level":"INFO","logger":"pagebound","msg":"request","request_id":"a1414240553a48f2b058e57224da8ffe","method":"GET","path":"/","route":"/","status":200,"duration_ms":1.1,"client":"172.17.0.1"}
--- the largest layers:
8.19kB	RUN |1 APP_VERSION=1.0.0 /bin/sh -c mkdir /d…
32.8kB	COPY app ./app # buildkit
23.2MB	RUN /bin/sh -c pip install -r requirements.t…
12.3kB	COPY requirements.txt . # buildkit
```

Things to notice: the **health status** moved from `starting` to `healthy` by itself (the Dockerfile's `HEALTHCHECK`); the process runs as the user `app`, not root; the logs are JSON; and the biggest layers are the base image and the `pip install`. The `/orders` data is stored in `/data` inside this container, which is not yet a named volume, so `docker rm` would erase it. Compose adds the volume in section 6.

### 5.5 `SIGTERM` again: exec form versus shell form

The Dockerfile uses the **exec form** of `CMD` (a JSON list). The **shell form** (`CMD uvicorn app.main:create_app ...`) wraps the command in `/bin/sh -c`, and `sh` becomes PID 1; it does not forward `SIGTERM` to Uvicorn, so the same problem as section 4.3 appears even though Uvicorn itself would handle it. Seeing it once makes it stick:

```bash run
printf 'FROM pagebound-api:1.0.0\nCMD uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000\n' > Dockerfile.shellform
docker build -q -f Dockerfile.shellform -t pbtut-shellform . > /dev/null
docker run -d --name pbtut-shell pbtut-shellform > /dev/null
sleep 3
now() { python3 -c "import time; print(time.time())"; }

start=$(now); docker stop -t 3 pbtut-api > /dev/null; end=$(now)
python3 -c "print('exec form : stopped at once, graceful shutdown ran:', $end - $start < 1.5)"
docker logs pbtut-api 2>&1 | grep -c "shutting down" | sed 's/^/  "shutting down" lines in the log: /'

start=$(now); docker stop -t 3 pbtut-shell > /dev/null; end=$(now)
python3 -c "print('shell form: sh swallowed the signal; docker had to wait out the grace period:', $end - $start >= 3.0)"
docker logs pbtut-shell 2>&1 | grep -c "shutting down" | sed 's/^/  "shutting down" lines in the log: /'

docker rm pbtut-api pbtut-shell > /dev/null
docker rmi pbtut-shellform > /dev/null
rm Dockerfile.shellform
```
```text
exec form : stopped at once, graceful shutdown ran: True
  "shutting down" lines in the log: 1
shell form: sh swallowed the signal; docker had to wait out the grace period: True
  "shutting down" lines in the log: 0
```

The exec form gave the application its chance to run the shutdown code (the `shutting down` log line, readiness turning red); the shell form had it killed without any notice.

### 5.6 Good image habits

- **Pin versions**: `python:3.14-slim` moves with patch releases. For reproducible builds pin more tightly (`python:3.14.4-slim`) or by digest (`@sha256:...`), and update on purpose. Pin Python dependencies exactly (done) and consider a lock file with hashes for tight control.
- **Tag with something meaningful**: the release version (`1.4.2`) and the git commit (`sha-3f9a1c2`). **Never deploy `latest`**: it is just another movable tag, and "which version is running?" has no answer. An image tag you deploy should be **immutable** in practice (never re-pushed under the same name).
- **One process per container**, logging to stdout, no `ssh` inside, no cron inside: the platform restarts, schedules and collects.
- **Small is good**: fewer packages mean fewer vulnerabilities and faster pulls. *Multi-stage builds* compile in a big builder image and copy only the result into a small final image; useful when you need compilers (`gcc`) to build a dependency, which you then do not want in production:

```dockerfile
# stage 1: build wheels with compilers available
FROM python:3.14-slim AS build
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# stage 2: the small runtime image gets only the wheels
FROM python:3.14-slim
COPY --from=build /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels
```

- **Scan for known vulnerabilities** (`trivy image pagebound-api:1.0.0`, or `docker scout`) in CI, and rebuild regularly to pick up base-image fixes.
- **Never put secrets in the image** (section 3.5). `docker history` shows every `ENV`, `ARG` and `RUN` of an image.

> **Try it on your machine**: push the image to a registry so that servers can pull it. With the free GitHub Container Registry (using your **personal** GitHub account):
>
> ```bash
> echo "$GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin   # a token with the write:packages scope
> docker tag pagebound-api:1.0.0 ghcr.io/YOUR_GITHUB_USER/pagebound-api:1.0.0
> docker push ghcr.io/YOUR_GITHUB_USER/pagebound-api:1.0.0
> ```
>
> `login` prints `Login Succeeded`; `push` prints one line per layer ending with `Pushed` (or `Layer already exists` for layers the registry has), and finally a `digest: sha256:...` line. Section 11 lets CI do this automatically.

### Try it: why is this Dockerfile slow?

```dockerfile
FROM python:3.14-slim
COPY . /srv
WORKDIR /srv
RUN pip install -r requirements.txt
CMD python -m uvicorn app.main:create_app --factory --host 0.0.0.0
```

A one-line code change takes 40 seconds to rebuild, and `docker stop` takes 10 seconds. List the problems.

<details><summary>Answer</summary>

(1) `COPY . /srv` comes **before** `pip install`, so any file change invalidates the install layer: copy `requirements.txt` first, install, then copy the code. (2) The shell-form `CMD` makes `sh` PID 1, which swallows `SIGTERM`: use the exec form (JSON list). (3) No `.dockerignore`, so `.git`, `.venv`, `.env` and databases are sent to the build and may end up in the image. (4) It runs as root: add a user. (5) No `HEALTHCHECK` and no pinned image version. (6) `--host` is missing the port and the app is bound to a default that may not be what the platform expects.

</details>

### Try it: what is in the image?

You committed `.env` (with `APP_SECRET_KEY=...`) by mistake, and the Dockerfile has `COPY . .`. You add `RUN rm .env` on the next line. Is the secret gone from the image?

<details><summary>Answer</summary>

No. Each instruction creates a layer, and the layer from `COPY . .` still contains `.env`; the `rm` only hides it in a later layer. Anyone with the image can extract the earlier layer. The only fix is to never copy it (list `.env` in `.dockerignore`), and to rotate the secret, because it has already been exposed (swe.07 section 15).

</details>

## 6. Docker Compose: several containers as one system

### 6.1 Why Compose

A real service is rarely one container: the API, a cache, a database, a proxy. Starting them with separate long `docker run` commands is error-prone. **Docker Compose** lets you describe the whole system in one file, `compose.yaml`, and start, stop and inspect it with a single command. The same file documents how your system fits together, and it runs identically on every developer's machine, in CI and on a small server.

### 6.2 The file

Our first version has two services, the API and Redis. (The proxy comes in section 7.) Read the file from top to bottom:

```yaml
# compose.yaml
name: pbtut                          # the project name; containers are named pbtut-<service>-<n>

services:
  api:
    build:
      context: .
      args:
        APP_VERSION: ${APP_VERSION:-dev}      # ${VAR:-default}: read from the shell or the .env file, else "dev"
    image: pagebound-api:${APP_VERSION:-dev}
    environment:
      APP_ENV: production
      APP_VERSION: ${APP_VERSION:-dev}
      APP_SECRET_KEY: ${APP_SECRET_KEY:?set APP_SECRET_KEY in the .env file}     # ":?" stops with this message if unset
      REDIS_URL: redis://redis:6379/0          # "redis" is the service name below: Compose's own DNS
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    volumes:
      - api-data:/data                         # the database survives container re-creation
    ports:
      - "127.0.0.1:${PUBLIC_PORT:-18080}:8000"
    depends_on:
      redis:
        condition: service_healthy             # start the API only after Redis answers its health check
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--save", "", "--appendonly", "no"]   # here Redis is only a counter store: no persistence
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 2s
      retries: 5
    restart: unless-stopped

volumes:
  api-data:
```

| Key | Meaning |
|---|---|
| `services` | one entry per container type |
| `build` / `image` | build from a Dockerfile here, and tag the result; or use a ready image (`redis:7-alpine`) |
| `environment` | variables set inside the container; `${...}` are substituted by Compose from your shell or the `.env` file |
| `volumes` | named volumes (declared at the bottom) or bind mounts |
| `ports` | publish ports to the host; `127.0.0.1:` keeps them local |
| `depends_on` with `condition: service_healthy` | start order **and** wait for the dependency to be healthy (plain `depends_on` only waits for "started", which is not "ready") |
| `healthcheck` | how Compose/Docker decide a container is healthy |
| `restart` | the restart policy from section 4.6 |
| `name` | the project name; it prefixes container, network and volume names (`pbtut_api-data`) |

The secret goes into a `.env` file next to `compose.yaml` that Compose reads for the `${...}` substitutions. We generate a random one now, and commit only an example:

```bash run
printf 'APP_SECRET_KEY=%s\nAPP_VERSION=1.0.0\n' "$(python -c 'import secrets; print(secrets.token_urlsafe(40))')" > .env
printf 'APP_SECRET_KEY=change-me-to-a-long-random-string\nAPP_VERSION=1.0.0\n' > .env.example
git init -q . 2>/dev/null; printf '.env\ncerts/\nbackups/\n' > .gitignore
echo "git ignores .env:"; git check-ignore -v .env
docker compose config --quiet && echo "compose file is valid"
```
```text
git ignores .env:
.gitignore:1:.env	.env
compose file is valid
```

`docker compose config` validates the file and prints the fully resolved version (with all variables substituted), the first thing to run when something does not work as expected. Because of the `:?` in the file, it also refuses to continue without `APP_SECRET_KEY`: a safe default.

### 6.3 Tutorial: the daily commands

```bash run
docker compose up -d --build 2>&1 | sed -E 's/[0-9.]+s$//' | grep -E "Container|Volume|Network" | sed -E 's/ +$//' | sort | uniq
echo "--- ps"
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}' | sed -E 's/Up [0-9]+ (seconds?|minutes?)/Up N seconds/'
```
```text
 Container pbtut-api-1 Created
 Container pbtut-api-1 Creating
 Container pbtut-api-1 Started
 Container pbtut-api-1 Starting
 Container pbtut-redis-1 Created
 Container pbtut-redis-1 Creating
 Container pbtut-redis-1 Healthy
 Container pbtut-redis-1 Started
 Container pbtut-redis-1 Starting
 Container pbtut-redis-1 Waiting
 Network pbtut_default Created
 Network pbtut_default Creating
 Volume pbtut_api-data Created
 Volume pbtut_api-data Creating
--- ps
SERVICE   STATUS                                     PORTS
api       Up Less than a second (health: starting)   127.0.0.1:18080->8000/tcp
redis     Up N seconds (healthy)                     6379/tcp
```

`up -d --build` builds images if needed and starts everything in the background, in dependency order (note that Redis became `Healthy` before the API was `Started`; you can see it in the output above). Now use it:

```bash run
sleep 2
for i in 1 2 3; do curl -s localhost:18080/hits | jq -c '{hits, store}'; done
echo "--- restart the API container; the counter lives in Redis, so it continues:"
docker compose restart api > /dev/null 2>&1
for i in $(seq 1 15); do curl -fs localhost:18080/readyz > /dev/null 2>&1 && break; sleep 1; done
curl -s localhost:18080/hits | jq -c '{hits, store}'
echo "--- look inside redis:"
docker compose exec redis redis-cli get pagebound:hits
echo "--- the application's own logs, last 2 lines, JSON parsed:"
docker compose logs api --no-log-prefix --tail 20 | grep '^{' | tail -2 | jq -c '{level, msg, status, route}'
```
```text
{"hits":1,"store":"redis"}
{"hits":2,"store":"redis"}
{"hits":3,"store":"redis"}
--- restart the API container; the counter lives in Redis, so it continues:
{"hits":4,"store":"redis"}
--- look inside redis:
4
--- the application's own logs, last 2 lines, JSON parsed:
{"level":"INFO","msg":"starting","status":null,"route":null}
{"level":"INFO","msg":"request","status":200,"route":"/hits"}
```

The counter continued from 3 to 4 across an API restart because its value is in **Redis**, a separate container: this is the "stateless processes, state in backing services" rule of section 1.3 in action. Had the counter been a variable in the API process (it is, when `REDIS_URL` is unset), a restart would have reset it.

| Command | Use |
|---|---|
| `docker compose up -d [--build] [service]` | create/update and start in the background |
| `docker compose ps` | status and health of the services |
| `docker compose logs [-f] [--tail N] [service]` | logs, optionally following |
| `docker compose exec service CMD` | run a command in a running container |
| `docker compose run --rm service CMD` | run a one-off container (migrations, scripts) |
| `docker compose restart service`, `stop`, `start` | control without re-creating |
| `docker compose up -d --scale api=3` | run several copies of a service |
| `docker compose config` | show the resolved configuration |
| `docker compose down` | stop and remove containers and the network (**keeps** volumes) |
| `docker compose down -v` | also delete the volumes (**destroys data**) |

### 6.4 What Compose gives you, and what it does not

Compose is excellent for development, CI and single-server deployments. It does **not** spread containers over several machines, restart them on another machine when one dies, or do rolling updates with zero downtime; orchestrators like Kubernetes, Nomad or managed services (AWS ECS, Google Cloud Run, Fly.io, Render) do. The images, health checks, environment variables and logs you build here carry over to all of them unchanged, which is why they are the part worth learning first.

### Try it: dependencies and readiness

Why does the file say `condition: service_healthy` instead of just `depends_on: [redis]`? What would happen on a slow machine without it?

<details><summary>Answer</summary>

Plain `depends_on` only orders the *start* of the containers: the API starts as soon as Redis' process has started, perhaps a second before Redis accepts connections. The API's first requests (or its readiness check) then fail, and the container may report unhealthy or crash at start-up. Waiting for the health check removes that race. (A robust app also retries its connections: dependencies can restart at any time, not only at boot.)

</details>

### Try it: `down` or `down -v`?

You want to restart the whole system with a clean slate for the *code*, but keep the order data. Which command do you use, and what would the other one do?

<details><summary>Answer</summary>

`docker compose down` followed by `up -d` removes and re-creates the containers and network but **keeps** the named volume `api-data`, so the orders remain. `docker compose down -v` also deletes the volumes: the database is gone. Treat `-v` like `rm -rf` on your data: never in production, and never from muscle memory.

</details>

## 7. Nginx: the front door

### 7.1 What a reverse proxy is for

Your API server (Uvicorn, Gunicorn) is good at running Python. It is not designed to face the open internet. A **reverse proxy** sits in front and takes care of the things servers should not do themselves:

| Job | Why in the proxy |
|---|---|
| **TLS** (HTTPS) termination | one place for certificates; the app speaks plain HTTP inside |
| **Load balancing** | spread requests across several app copies; skip dead ones |
| **Slow clients and buffering** | Nginx absorbs slow uploads and downloads so your workers do not wait on them |
| **Static files and caching** | serve images and CSS without waking Python |
| **Request limits** | body size, rate limits, timeouts |
| **Compression, headers** | gzip, security headers |
| **Request IDs and access logs** | one place that sees every request |

**Nginx** is the most common choice (others: Caddy, which obtains HTTPS certificates automatically; Traefik; HAProxy; cloud load balancers). You do not install it: we run the official image.

### 7.2 Nginx configuration in one page

An Nginx config is a tree of **blocks** containing **directives** ending in `;`. The pieces you need for a proxy:

```text
http {                      # (the image's main file already contains this and includes conf.d/*.conf)
    upstream ... { }        # optional: a named group of backend servers
    server {                # one virtual host
        listen 80;
        server_name example.com;
        location / {        # rules for URLs starting with "/"
            proxy_pass http://api:8000;
        }
    }
}
```

With the official image you write the `server` blocks in a file mounted at `/etc/nginx/conf.d/default.conf`. Our first version proxies everything to the API and writes **JSON access logs containing a request id**:

```nginx
# nginx/default.conf
# one JSON object per request; request_id is made by nginx for every request
log_format json_log escape=json
    '{"ts":"$time_iso8601","remote":"$remote_addr","method":"$request_method","uri":"$request_uri",'
    '"status":$status,"bytes":$body_bytes_sent,"duration":$request_time,"upstream":"$upstream_addr",'
    '"upstream_status":"$upstream_status","request_id":"$request_id"}';

server {
    listen 80;
    access_log /dev/stdout json_log;
    client_max_body_size 1m;

    location / {
        proxy_pass http://api:8000;                          # "api" is the Compose service name
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;           # the app logs this same id
        proxy_connect_timeout 2s;
        proxy_read_timeout 5s;
    }

    location = /nginx-health {
        access_log off;
        return 200 "ok\n";
    }
}
```

| Directive | Meaning |
|---|---|
| `log_format ... escape=json` | defines a log line layout; `$request_id` is a unique id Nginx makes per request |
| `listen`, `server_name` | which port and host name this server block answers |
| `client_max_body_size` | largest request body; bigger ones get `413` |
| `proxy_pass` | send the request to this backend |
| `proxy_set_header` | headers for the backend. **`Host`, `X-Forwarded-For` and `X-Forwarded-Proto` let the app know the real client and scheme** (otherwise it sees only the proxy) |
| `proxy_connect_timeout`, `proxy_read_timeout` | how long to wait for the backend to accept and to answer; slow answers become `504` |
| `location = /nginx-health` | an exact-match location (Nginx's own liveness probe) |

Now change Compose: the API is no longer published to the host (only the proxy is), and an `nginx` service is added. These two edits show the whole change:

```diff
# compose.yaml
-     ports:
-       - "127.0.0.1:${PUBLIC_PORT:-18080}:8000"
-     depends_on:
+     depends_on:
```

```diff
# compose.yaml
- volumes:
-   api-data:
+   nginx:
+     image: nginx:alpine
+     ports:
+       - "127.0.0.1:${PUBLIC_PORT:-18080}:80"
+     volumes:
+       - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
+     depends_on:
+       api:
+         condition: service_healthy
+     restart: unless-stopped
+
+ volumes:
+   api-data:
```

Validate the Nginx configuration **before** loading it (this is the habit that prevents outages), apply it, and make requests through the proxy:

```bash run
docker compose up -d 2>&1 | grep -E "Started|Recreated|Running" | sed -E 's/ +$//' | sort | uniq
sleep 3
docker compose exec nginx nginx -t 2>&1
echo "--- through the proxy:"
curl -s localhost:18080/ | jq -c 'del(.instance)'
echo "--- the response headers of a request:"
curl -si localhost:18080/orders/1 | grep -iE "^HTTP|^server|^x-request-id|^content-type" | tr -d '\r'
echo "--- the access log line nginx wrote (JSON):"
docker compose logs nginx --no-log-prefix --tail 1 | jq -c 'del(.ts, .remote, .upstream, .duration)'
```
```text
 Container pbtut-api-1 Recreated
 Container pbtut-api-1 Started
 Container pbtut-nginx-1 Started
 Container pbtut-redis-1 Running
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
--- through the proxy:
{"service":"pagebound","version":"1.0.0","env":"production"}
--- the response headers of a request:
HTTP/1.1 404 Not Found
Server: nginx/1.31.6
Content-Type: application/json
x-request-id: 2bd7f8f0a1ca53e9fbc29657746c07fa
--- the access log line nginx wrote (JSON):
{"method":"GET","uri":"/orders/1","status":404,"bytes":28,"upstream_status":"404","request_id":"2bd7f8f0a1ca53e9fbc29657746c07fa"}
```

`nginx -t` says `syntax is ok` and `test is successful`; run it every time you edit the configuration, and use `nginx -s reload` (not a restart) to apply it without dropping connections. Notice the request id in the response header: it was made by Nginx, passed to the app in `X-Request-ID`, and returned by the app.

### 7.3 Load balancing, and the DNS trap

Run three copies of the API. Docker's DNS name `api` now resolves to three addresses and Nginx can spread requests across them:

```bash run
docker compose up -d --scale api=3 --no-recreate 2>&1 | grep -cE "Started|Running" | sed 's/^/containers started or running: /'
for i in $(seq 1 40); do curl -fs localhost:18080/readyz > /dev/null && break; sleep 1; done
sleep 3
echo "--- 12 requests; how many different API instances answered?"
for i in $(seq 1 12); do curl -s localhost:18080/whoami | jq -r .instance; done | sort | uniq | wc -l | sed 's/^/distinct instances: /'
```
```text
containers started or running: 5
--- 12 requests; how many different API instances answered?
distinct instances: 1
```

You would expect 3. The answer depends on a subtle Nginx behaviour: with `proxy_pass http://api:8000;` written literally, **Nginx resolves the name once, when it loads the configuration**. The configuration was loaded when only one API container existed, so Nginx keeps sending to that one address; the new containers receive nothing. A reload makes Nginx resolve again:

```bash run
docker compose exec nginx nginx -s reload > /dev/null 2>&1 && echo "nginx reloaded"
sleep 1
for i in $(seq 1 12); do curl -s localhost:18080/whoami | jq -r .instance; done | sort | uniq | wc -l | sed 's/^/after a reload, distinct instances: /'
```
```text
nginx reloaded
after a reload, distinct instances: 3
```

This explains a famous class of production surprises ("we scaled up and nothing changed" and "we redeployed the API and Nginx kept sending to the old address, giving 502"). There are two cures: reload Nginx after every change of the backend, or make Nginx re-resolve by itself. The second is done with Docker's internal DNS server (`127.0.0.11`) and a **variable** in `proxy_pass`, which forces name resolution at request time:

```diff
# nginx/default.conf
-     location / {
-         proxy_pass http://api:8000;                          # "api" is the Compose service name
+     # Docker's internal DNS; look the name up again every 5 seconds so new or replaced API containers are found
+     resolver 127.0.0.11 valid=5s;
+     set $backend http://api:8000;
+
+     location / {
+         proxy_pass $backend;                                 # a variable: resolved at request time, not at load time
```

```bash run
docker compose exec nginx nginx -t 2>&1 | tail -1
docker compose exec nginx nginx -s reload > /dev/null 2>&1 && echo "nginx reloaded"
sleep 1
for i in $(seq 1 12); do curl -s localhost:18080/whoami | jq -r .instance; done | sort | uniq | wc -l | sed 's/^/distinct instances: /'
echo "--- replace one API container; no nginx reload needed:"
docker compose up -d --force-recreate --no-deps --scale api=3 api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
sleep 6
for i in $(seq 1 12); do curl -s -o /dev/null -w '%{http_code}\n' localhost:18080/whoami; done | sort | uniq -c
```
```text
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx reloaded
distinct instances: 3
--- replace one API container; no nginx reload needed:
     12 200
```

### 7.4 When the backend is down: 502 and 504

Two errors you will read in Nginx logs for years:

| Status | Meaning | Usual cause |
|---|---|---|
| **502 Bad Gateway** | Nginx could not get a valid answer from the backend | the app is down, crashed, restarting, or Nginx points at a stale address |
| **504 Gateway Timeout** | the backend accepted but did not answer within `proxy_read_timeout` | a slow request, a stuck worker, an overloaded database |
| **413 Request Entity Too Large** | the body is bigger than `client_max_body_size` | an upload |
| **499** (Nginx only, in the log) | the client gave up and closed the connection before the answer | slow responses, impatient users |

See both happen, with three API replicas running behind the proxy:

```bash run
docker compose stop api > /dev/null 2>&1
echo "backend stopped      : $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/)"
docker compose logs nginx --no-log-prefix --tail 1 | jq -c '{status, upstream_status}'
docker compose start api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
echo "backend started again: $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/)"
echo "--- a slow request: the app needs 8 s, nginx waits at most 5 s per attempt"
curl -s -o /dev/null -w "client got status %{http_code}\n" -m 40 "localhost:18080/slow?seconds=8"
docker compose logs nginx --no-log-prefix --tail 1 | jq -c '{status, upstream_status, longer_than_10s: (.duration > 10)}'
```
```text
backend stopped      : 504
{"status":504,"upstream_status":"504, 504, 504"}
backend started again: 200
--- a slow request: the app needs 8 s, nginx waits at most 5 s per attempt
client got status 504
{"status":504,"upstream_status":"504, 504, 504","longer_than_10s":true}
```

Two surprises, both worth remembering:

1. **A stopped backend gave 504, not 502.** Nginx still knew the old container addresses (the resolver caches an answer for 5 seconds), and connecting to an address nobody answers on does not fail at once: it times out after `proxy_connect_timeout`. The log field `upstream_status` shows `"504, 504, 504"`: Nginx tried all three addresses. A 502 appears when the connection is *refused immediately* (the machine is up but nothing listens on the port, as when the app process has crashed inside a still-running container) or the answer is malformed.
2. **Nginx retried the slow request on the other replicas.** For idempotent requests (such as `GET`), the default `proxy_next_upstream error timeout` moves on to the next server after an error *or a timeout*. The slow request therefore ran **three times**, and the client waited three times 5 seconds. For endpoints that are slow or have costly side effects set `proxy_next_upstream off;` (or `proxy_next_upstream_tries 1;`) so a timeout is reported instead of multiplied. `POST` requests are not retried by default, which is the safe choice.

### 7.5 Rate limiting at the proxy

Nginx can refuse excessive requests before they reach Python (swe.07 section 11 built the algorithm; here is the production tool). `limit_req_zone` defines a shared counter keyed by client address; `limit_req` applies it:

```diff
# nginx/default.conf
- server {
-     listen 80;
+ limit_req_zone $binary_remote_addr zone=per_ip:10m rate=20r/s;      # 20 requests per second per client address
+
+ server {
+     listen 80;
```

```diff
# nginx/default.conf
-         proxy_pass $backend;                                 # a variable: resolved at request time, not at load time
+         limit_req zone=per_ip burst=40 nodelay;              # allow bursts of 40 beyond 20/s; refuse the rest with 503
+         proxy_pass $backend;                                 # a variable: resolved at request time, not at load time
```

```bash run
docker compose exec nginx nginx -t 2>&1 | tail -1
docker compose exec nginx nginx -s reload > /dev/null 2>&1 && echo "nginx reloaded"
sleep 1
echo "150 requests as fast as curl can send them:"
for i in $(seq 1 150); do curl -s -o /dev/null -w '%{http_code}\n' localhost:18080/healthz; done | sort | uniq -c | awk '{print "  " $1 " x HTTP " $2}'
```
```text
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx reloaded
150 requests as fast as curl can send them:
  68 x HTTP 200
  82 x HTTP 503
```

You should see mostly `200` and a number of `503` (the exact numbers depend on how fast your machine sends requests). Nginx uses `503` by default for a limited request (`limit_req_status 429;` changes it to the more accurate 429). Behind a proxy, remember the lesson of swe.07: the limit sees the address Nginx sees, so if another proxy sits in front, configure `real_ip`.

### 7.6 HTTPS with a certificate you made yourself

Real certificates come from a certificate authority such as **Let's Encrypt** (free, automated with `certbot` or built into Caddy). To learn the mechanics without a domain name, make a **self-signed** certificate with OpenSSL; browsers will warn about it, because nobody they trust signed it, but the encryption is real.

```bash run
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -nodes -days 30 -keyout certs/dev.key -out certs/dev.crt \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null
openssl x509 -in certs/dev.crt -noout -subject -issuer -ext subjectAltName | sed 's/^ *//'
```
```text
subject=CN=localhost
issuer=CN=localhost
X509v3 Subject Alternative Name: 
DNS:localhost, IP Address:127.0.0.1
```

Now a second `server` block that listens on 443 with the certificate, and a redirect from port 80:

```diff
# nginx/default.conf
- server {
-     listen 80;
-     access_log /dev/stdout json_log;
+ server {
+     listen 443 ssl;
+     ssl_certificate     /etc/nginx/certs/dev.crt;
+     ssl_certificate_key /etc/nginx/certs/dev.key;
+     ssl_protocols       TLSv1.2 TLSv1.3;
+     access_log /dev/stdout json_log;
+     client_max_body_size 1m;
+     resolver 127.0.0.11 valid=5s;
+     set $backend http://api:8000;
+     location / {
+         proxy_pass $backend;
+         proxy_set_header Host $host;
+         proxy_set_header X-Forwarded-Proto https;
+         proxy_set_header X-Real-IP $remote_addr;
+         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
+         proxy_set_header X-Request-ID $request_id;
+     }
+ }
+
+ server {
+     listen 80;
+     location / { return 301 https://$host:18443$request_uri; }   # send plain HTTP to HTTPS
+ }
+
+ server {
+     listen 8080;                                             # internal plain-HTTP server used by the rest of this chapter
+     access_log /dev/stdout json_log;
```

```diff
# compose.yaml
-     ports:
-       - "127.0.0.1:${PUBLIC_PORT:-18080}:80"
-     volumes:
-       - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
+     ports:
+       - "127.0.0.1:${PUBLIC_PORT:-18080}:8080"      # plain HTTP, used by the rest of this chapter
+       - "127.0.0.1:18081:80"                          # redirects to HTTPS
+       - "127.0.0.1:18443:443"
+     volumes:
+       - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
+       - ./certs:/etc/nginx/certs:ro
```

```bash run
docker compose up -d nginx 2>&1 | grep -E "Recreated|Started" | sed -E 's/ +$//' | sort | uniq
sleep 2
docker compose exec nginx nginx -t 2>&1 | tail -1
echo "--- HTTPS (-k accepts our self-signed certificate):"
curl -sk https://localhost:18443/ | jq -c 'del(.instance)'
curl -skv https://localhost:18443/healthz 2>&1 | grep -E "SSL connection using|subject:|issuer:" | sed 's/^\* *//'
echo "--- without -k, curl refuses, as a browser would warn:"
curl -s -o /dev/null -w "exit code %{exitcode}\n" https://localhost:18443/ ; true
echo "--- plain HTTP is redirected to HTTPS:"
curl -si localhost:18081/orders/1 | grep -iE "^HTTP|^location" | tr -d '\r'
echo "--- the internal plain-HTTP port (used by the rest of this chapter) still works:"
curl -s localhost:18080/healthz
```
```text
 Container pbtut-nginx-1 Recreated
 Container pbtut-nginx-1 Started
nginx: configuration file /etc/nginx/nginx.conf test is successful
--- HTTPS (-k accepts our self-signed certificate):
{"service":"pagebound","version":"1.0.0","env":"production"}
SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519MLKEM768 / RSASSA-PSS
subject: CN=localhost
issuer: CN=localhost
--- without -k, curl refuses, as a browser would warn:
exit code 60
--- plain HTTP is redirected to HTTPS:
HTTP/1.1 301 Moved Permanently
Location: https://localhost:18443/orders/1
--- the internal plain-HTTP port (used by the rest of this chapter) still works:
{"status":"alive"}
```

The mechanics are the same with a real certificate: Nginx holds the private key and certificate (in production from Let's Encrypt, renewed automatically about every 60 days), terminates TLS, and speaks plain HTTP to the app over the private network. Add `Strict-Transport-Security` headers once HTTPS works everywhere (swe.07 section 14.9), and never serve both a login page and its form over plain HTTP.

> **Try it on your machine** (needs a server with a public IP and a domain name; not run here): get a real certificate.
>
> ```bash
> sudo apt install certbot python3-certbot-nginx           # on a server where nginx runs on the host
> sudo certbot --nginx -d shop.example.com                  # edits your nginx config and installs the certificate
> sudo certbot renew --dry-run                              # proves automatic renewal works
> ```
>
> `certbot` asks for an e-mail address and to agree to the terms, proves you control the domain by answering a challenge on port 80, and prints "Congratulations! You have successfully enabled HTTPS". The final `--dry-run` line should say "Congratulations, all simulated renewals succeeded". Domain names, paths and dates will be yours.

### 7.7 Cheat sheet and common problems

| Task | Command |
|---|---|
| check the config | `nginx -t` |
| apply a change without downtime | `nginx -s reload` |
| see the effective config | `nginx -T` |
| follow logs | `docker compose logs -f nginx` |

| Symptom | First thing to check |
|---|---|
| 502 right after a deploy | stale upstream address (section 7.3); is the app healthy? |
| 504 on long requests | `proxy_read_timeout`; move long work to a queue (swe.08) |
| 413 on uploads | `client_max_body_size` |
| the app thinks every user has the same IP, or uses `http://` links | missing `X-Forwarded-For` / `X-Forwarded-Proto` and an app that does not trust them (`--proxy-headers`) |
| config change has no effect | forgot `nginx -s reload`; or edited a file that is not the mounted one |
| redirect loop after enabling HTTPS | the app does not know the original scheme (`X-Forwarded-Proto`) |

### Try it: read the log

An access log line says `"status":502, "upstream":"172.19.0.3:8000", "upstream_status":"-"`. What does `-` for `upstream_status` tell you, and what do you check first?

<details><summary>Answer</summary>

Nginx never got a status from the upstream at all: it could not connect (or the connection broke before a response). The backend at that address is down, restarting, or gone (a stale address from before a redeploy). Check `docker compose ps` for the API container's state and health, its logs for a crash, and whether Nginx resolves the name again (section 7.3).

</details>

### Try it: design the limits

The login endpoint needs a much stricter rate limit than the rest of the API. How would you configure it in Nginx, and why is that not enough on its own?

<details><summary>Answer</summary>

Add a second `limit_req_zone` (for example `rate=5r/m`) and apply it in a `location = /login` block with its own `limit_req`. It is not enough alone because the proxy only sees client addresses: an attacker with many addresses, or many users behind one office address, defeats or hurts it. Keep the per-account throttling and lockout logic in the application (swe.07 section 11.5) as well.

</details>


## 8. Structured logs and request IDs

This section delivers the first outcome of the chapter: **trace one failing request through the logs using its request ID.**

### 8.1 From text to events

A beginner's log line is a sentence: `User ada failed to log in from 10.0.0.9`. It is easy to read and hard to search: you need a regular expression to extract the user, and the wording changes with the programmer. A **structured log** records an **event with named fields**, one JSON object per line:

```json
{"ts":"2026-11-09T07:13:20.115Z","level":"INFO","logger":"pagebound","msg":"request","request_id":"demo-req-0001","method":"GET","path":"/boom","status":500,"duration_ms":21.8}
```

A machine (the `jq` tool, a log database, your monitoring system) can now answer "show every 500 on `/boom` slower than 100 ms" without guessing at wording. The rules:

- **One event per line, as JSON, on standard output** (the platform collects stdout; the app does not manage log files).
- **Fixed field names** (`ts`, `level`, `msg`, `request_id`, ...), and **extra fields for the facts** (`order_id`, `status`, `duration_ms`) instead of formatting them into the message. Keep `msg` a short constant such as `"order created"`.
- **UTC timestamps** in ISO 8601 format, with the time zone in the value.
- **Levels with meaning:** `DEBUG` (development detail), `INFO` (normal events worth keeping), `WARNING` (odd but handled), `ERROR` (an operation failed), `CRITICAL` (the service is in trouble).
- **Log what happened, not what you hope**: the *outcome* (status, duration, ids), not every variable.
- **Never log secrets or personal data** (passwords, tokens, full card numbers; swe.07 section 15.6), and think before logging whole request bodies.
- **Do not log health probes**: a check every 5 seconds from each of 20 containers would bury the real events. The service skips `/healthz`, `/readyz` and `/metrics`.

### 8.2 The request ID

When a user reports "my order failed", you have a needle and a haystack: millions of log lines from several containers. A **request ID** is the thread through the haystack: a unique string created when a request enters the system and attached to **every** log line produced because of it, and returned to the client. The rules:

1. Create it at the **edge** (our Nginx makes `$request_id`). If an id arrives from a trusted proxy, reuse it; otherwise generate one.
2. **Validate** an incoming id (length, characters) before trusting it. A client-controlled value in your logs can contain newlines or enormous text (log injection, swe.07 section 15.6). The middleware accepts only `[A-Za-z0-9._-]{8,64}` and otherwise makes its own.
3. Carry it through the code with a **context variable** (`contextvars`), so every `log.info(...)` anywhere includes it without passing it around as an argument. Each request (each async task) sees its own value.
4. **Return it** in a response header (`X-Request-ID`) and in error bodies, so a user or support person can quote it.
5. **Pass it on** to everything the request causes: calls to other services (as a header), jobs put on a queue (in the payload, swe.08 section 15.2), database comments if you like.

You have already read the implementation in section 5: `request_id_var` in `logs.py` and the `RequestContext` middleware in `main.py`. This is the whole mechanism:

```text
 client --> nginx: makes id R, logs it         --> API: reads header X-Request-ID = R
                                                   sets request_id_var = R   (every log line now carries R)
                                                   ... on error: logs the traceback with R; answers {"request_id": R}
 client <-- X-Request-ID: R in the response headers and in the error body
```

### 8.3 `jq`, the tool for reading JSON logs

`jq` filters and reshapes JSON. A few forms cover most of what you need. First, bring the stack to a clean known state (one API container) and generate a realistic mix of traffic with a small script:

```bash run
cat > traffic.sh <<'SHEOF'
#!/usr/bin/env bash
# usage: ./traffic.sh   -> 20 order creations, 6 reads, 3 reads of a missing order, 1 slow request
BASE="${1:-http://127.0.0.1:18080}"
for i in $(seq 1 20); do
  curl -s -o /dev/null -X POST "$BASE/orders" -H 'content-type: application/json' -d "{\"item\": \"item-$i\", \"quantity\": $((i % 5 + 1))}"
done
for i in 1 2 3 4 5 6; do curl -s -o /dev/null "$BASE/orders/$i"; done
for i in 1 2 3; do curl -s -o /dev/null "$BASE/orders/9999"; done
curl -s -o /dev/null "$BASE/slow?seconds=0.6"
SHEOF
chmod +x traffic.sh
docker compose up -d --force-recreate --no-deps --scale api=1 api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
./traffic.sh
sleep 1
docker compose logs api --no-log-prefix 2>/dev/null | grep '^{' > app.log
echo "log lines captured: $(wc -l < app.log)"
head -1 app.log | jq -c 'del(.ts, .instance)'
```
```text
log lines captured: 51
{"level":"INFO","logger":"pagebound","msg":"starting","request_id":"-","version":"1.0.0","env":"production"}
```

Now the `jq` vocabulary, using the captured file (`app.log`). Read each command and its output:

```bash run
echo "--- 1. select: only the lines that match a condition (404s)"
jq -c 'select(.msg == "request" and .status == 404) | {method, path, status}' app.log | sort | uniq -c

echo "--- 2. pick fields: -r prints raw text instead of JSON"
jq -r 'select(.msg == "request") | "\(.status) \(.method) \(.route)"' app.log | sort | uniq -c

echo "--- 3. slurp (-s) turns all lines into one array, so we can group and count"
jq -sc '[.[] | select(.msg == "request")] | group_by(.status) | map({status: .[0].status, requests: length})' app.log

echo "--- 4. the slowest request"
jq -sc '[.[] | select(.msg == "request")] | max_by(.duration_ms) | {route, duration_ms: (.duration_ms | floor)}' app.log

echo "--- 5. average duration per route (milliseconds, rounded)"
jq -sc '[.[] | select(.msg == "request")] | group_by(.route) | map({route: .[0].route, n: length, avg_ms: ((map(.duration_ms) | add / length) | floor)}) | sort_by(.route)' app.log
```
```text
--- 1. select: only the lines that match a condition (404s)
      3 {"method":"GET","path":"/orders/9999","status":404}
--- 2. pick fields: -r prints raw text instead of JSON
      6 200 GET /orders/{order_id}
      1 200 GET /slow
     20 201 POST /orders
      3 404 GET /orders/{order_id}
--- 3. slurp (-s) turns all lines into one array, so we can group and count
[{"status":200,"requests":7},{"status":201,"requests":20},{"status":404,"requests":3}]
--- 4. the slowest request
{"route":"/slow","duration_ms":602}
--- 5. average duration per route (milliseconds, rounded)
[{"route":"/orders","n":20,"avg_ms":3},{"route":"/orders/{order_id}","n":9,"avg_ms":1},{"route":"/slow","n":1,"avg_ms":602}]
```

| `jq` form | Meaning |
|---|---|
| `.field`, `.a.b` | read a field |
| `select(condition)` | keep only matching items |
| `{a, b: .c}` | build a new object |
| `-c` / `-r` | compact output / raw text output |
| `-s` | read all inputs into one array ("slurp") |
| `group_by(.x)`, `map(...)`, `length`, `add`, `max_by(.x)`, `sort_by(.x)` | array tools |
| `del(.a, .b)` | remove fields |
| `--arg name value` | pass a shell value into the filter (use it instead of pasting values into the filter text) |

### 8.4 Tutorial: trace one failing request

The story. A customer writes: *"I clicked 'place order' and got an error. The page said the error id is `8fad38b4...`."* You have no other clue. Follow the id.

First we need such a failure. The `/boom` endpoint has a bug, as real code does. We make the request through the front door, and look at what the **client** receives:

```bash run
RESPONSE=$(curl -si localhost:18080/boom)
echo "$RESPONSE" | grep -iE "^HTTP|^x-request-id" | tr -d '\r' | sed -E 's/(x-request-id: )[0-9a-f]+/\1<REQUEST-ID>/I'
echo "$RESPONSE" | tail -1 | sed -E 's/"request_id":"[0-9a-f]+"/"request_id":"<REQUEST-ID>"/'
echo "$RESPONSE" | grep -i '^x-request-id' | awk '{print $2}' | tr -d '\r' > request_id.txt
echo "id saved ($(wc -c < request_id.txt) characters)"
```
```text
HTTP/1.1 500 Internal Server Error
x-request-id: <REQUEST-ID>
{"error":"internal error","request_id":"<REQUEST-ID>"}
id saved (33 characters)
```

The user sees only `internal error` and the id: **no traceback, no internals** (swe.07 section 9.4). Now we are the engineer with just the id. Step 1: the **proxy** log. Did the request arrive, what did Nginx get back, which backend served it?

```bash run
ID=$(cat request_id.txt)
echo "--- step 1: nginx's view"
docker compose logs nginx --no-log-prefix 2>/dev/null | grep '^{' | jq -c --arg id "$ID" 'select(.request_id == $id) | {method, uri, status, upstream_status}'
```
```text
--- step 1: nginx's view
{"method":"GET","uri":"/boom","status":500,"upstream_status":"500"}
```

Nginx says the request was `GET /boom` and the backend answered 500: the problem is in the application, not in the network or the proxy. Step 2: the **application** log for the same id. Every line the app wrote while handling that request carries it:

```bash run
ID=$(cat request_id.txt)
docker compose logs api --no-log-prefix 2>/dev/null | grep '^{' > app.log
echo "--- step 2: every application log line with this id"
jq -c --arg id "$ID" 'select(.request_id == $id) | {level, msg, status, route}' app.log
```
```text
--- step 2: every application log line with this id
{"level":"ERROR","msg":"unhandled error","status":null,"route":null}
{"level":"INFO","msg":"request","status":500,"route":"/boom"}
```

There are two lines: an `ERROR` named `unhandled error`, and the access line with status 500. The ERROR line holds the traceback. Step 3: **read it**:

```bash run
ID=$(cat request_id.txt)
echo "--- step 3: the traceback, last frames only"
jq -r --arg id "$ID" 'select(.request_id == $id and .level == "ERROR") | .exception' app.log | tail -3
```
```text
--- step 3: the traceback, last frames only
  File "/srv/app/main.py", line 133, in boom
    raise RuntimeError("simulated bug while building the invoice")
RuntimeError: simulated bug while building the invoice
```

The last frame names the file, the line and the exception: `main.py`, function `boom`, `RuntimeError: simulated bug while building the invoice`. You went from "the customer saw an error" to the line of code in four commands, **without asking the customer anything and without reproducing the bug**. The investigation pattern is always the same:

1. **Get the id** from the user, the error page, a support ticket or an alert.
2. **Search the edge** (proxy, load balancer) log: what status, which backend, how long?
3. **Search the application** log for the same id: what did it do, where did it fail?
4. **Widen if needed**: other services and workers touched by that request (same id), database slow-query logs, metrics for the time window (section 10).
5. **Fix, write a test that reproduces it, deploy** (sections 11 and 12).

Variations you will meet: the user has no id, only a time and an account (search the logs by `user_id` and time range, then take the id from the matching line); the id is not found anywhere (the request never reached you: check DNS, the load balancer, the client); the id is in the edge log but not in the app log (the proxy could not reach the app: a `502` with `upstream_status "-"`, section 7.4).

> **A design choice worth knowing.** Our Nginx always creates its own `$request_id`. If a load balancer in front of Nginx already assigns one (many cloud load balancers add `X-Request-ID` or `X-Amzn-Trace-Id`), you would rather **reuse** it so that the id is the same from the very first hop. Nginx can do that with a `map`: `map $http_x_request_id $req_id { default $http_x_request_id; "" $request_id; }`, then `proxy_set_header X-Request-ID $req_id;` and log `$req_id`. The app already validates what it receives, so a hostile client cannot do harm with a strange value.

### 8.5 Across services, workers and machines

One user action often touches several programs. Pass the id along everywhere: as the `X-Request-ID` header of outgoing HTTP calls, in the payload of queued jobs (`{"_meta": {"request_id": ...}}`, swe.08 section 15.2) and into the log context of the worker, so that `jq 'select(.request_id == $id)'` over **all** services' logs tells the whole story. This is the foundation of **distributed tracing** (OpenTelemetry and tools like Jaeger or Tempo): they add timing for each step (*spans*) and visualise the chain, but the idea is the same.

### 8.6 Where logs go, and the disk-full trap

Your program writes JSON to standard output. Docker's default **logging driver** (`json-file`) stores it in a file on the host, **with no size limit**. A chatty service can fill the disk and take the whole server down. Always set rotation:

```bash run
docker inspect --format 'log driver: {{.HostConfig.LogConfig.Type}}, options: {{.HostConfig.LogConfig.Config}}' "$(docker compose ps -q api | head -1)"
```
```text
log driver: json-file, options: map[]
```

(An empty options map means *unlimited*.) Set limits per service in Compose; here is the edit:

```diff
# compose.yaml
-       LOG_LEVEL: ${LOG_LEVEL:-INFO}
+       LOG_LEVEL: ${LOG_LEVEL:-INFO}
+     logging:
+       driver: json-file
+       options:
+         max-size: "10m"                        # rotate a log file at 10 MB...
+         max-file: "3"                          # ...and keep at most 3 files: 30 MB per container
```

```bash run
docker compose up -d --no-deps --scale api=1 api 2>&1 | grep -E "Recreated|Started" | sed -E 's/ +$//' | sort | uniq
docker inspect --format 'log driver: {{.HostConfig.LogConfig.Type}}, options: {{.HostConfig.LogConfig.Config}}' "$(docker compose ps -q api | head -1)"
```
```text
 Container pbtut-api-1 Recreated
 Container pbtut-api-1 Started
log driver: json-file, options: map[max-file:3 max-size:10m]
```

In production you ship the stream to a log system (Loki, Elasticsearch/OpenSearch, CloudWatch, Datadog) that stores, indexes and lets you search by field, with **retention** (keep 14 to 30 days, not for ever) and access control, since logs often contain sensitive facts.

| | Logs | Metrics | Traces |
|---|---|---|---|
| Question | what happened to *this* request? | how is the system behaving *overall*? | where did the time go *across services*? |
| Shape | events | numbers over time | a tree of timed steps |
| Cost | grows with traffic | constant per series | sampled |
| Tool in this chapter | `jq`, `docker compose logs` | Prometheus (section 10) | described only |

### Try it: follow the id yourself

Create three failing requests (`/boom`) and two `404`s with `curl -si`, note each `x-request-id`, and for each: find the nginx line, the app lines and the exception. Which one needed the traceback, and which did not?

<details><summary>Answer</summary>

The `/boom` requests have an `ERROR` line with a traceback (a server bug); the `404`s have only the access line with `status: 404` and no `ERROR` (a normal client mistake that the app handled). The status and level decide where to look: 5xx means read the traceback; 4xx means look at the request itself (path, validation errors) and ask whether the client or the contract is wrong.

</details>

### Try it: what is wrong with these log lines?

(a) `print(f"charging card {card_number} for {user.email}")`; (b) `log.error("failed: " + str(exc))` inside a handler that also returns the exception text to the client; (c) a log call in a loop that runs once per row of a 2-million-row import.

<details><summary>Answer</summary>

(a) It logs a card number and a personal e-mail address: sensitive data in a place many people can read, copied to backups and log vendors; log an id instead. (b) The message is built with string concatenation (no structured fields, nothing searchable except by text) and returning internals to the client leaks them (swe.07 section 9.4): log the exception with `log.exception(...)`, answer with the request id. (c) Two million lines hide the real events and cost money; log a summary every N rows or at the end with counts and duration.

</details>

## 9. Health checks

### 9.1 Three different questions

A platform that runs your containers (Docker, Kubernetes, a load balancer) wants to ask your service three different things, and the answers lead to three different actions:

| Check | Question | If it fails, the platform... |
|---|---|---|
| **Liveness** | is the process alive and not stuck? | **restarts** it |
| **Readiness** | can it serve traffic right now? | **stops sending traffic** to it (but leaves it running) |
| **Startup** | has it finished starting? | waits, and does not run the other checks yet |

Mixing them up causes classic outages. If your **liveness** check also tests the database, a database outage makes the platform restart every healthy application container at once, which cannot fix the database and makes the recovery slower (a *restart storm*). Liveness must answer only "is this process broken in a way a restart would fix?", so it checks nothing else. **Readiness** is where dependencies belong: "if I cannot reach my database, I should not receive requests, but I should not be killed either."

### 9.2 What the service does

The two endpoints in `main.py`:

- `GET /healthz` always answers `200 {"status": "alive"}`. If the event loop is blocked or the process is wedged, it will not answer, and that is exactly what liveness detects.
- `GET /readyz` checks what the service needs to do its work: it can open the database, it can reach Redis, and it is **not draining**. It answers `200` or `503` with the list of problems. When the process receives `SIGTERM`, the shutdown code sets `draining`, so readiness turns red before the process exits and a load balancer stops sending new requests (the first half of a graceful shutdown; finishing the requests already in flight is the second half).

Rules of thumb for health endpoints: keep them **fast and cheap** (a `SELECT 1`, a `PING`, with short timeouts, never a heavy query); do not require authentication, but expose them only on the **internal network** (they can reveal infrastructure details; return minimal data to the outside); never let a health check have side effects.

### 9.3 Docker and Compose health checks

Docker runs the `HEALTHCHECK` from the Dockerfile (section 5.2) every 5 seconds. It has three outcomes shown in `docker ps`: `(health: starting)` during `start_period`, `(healthy)`, and `(unhealthy)` after `retries` consecutive failures. Compose uses them for `depends_on: condition: service_healthy` (section 6) and `up --wait` (section 12).

An important fact: **plain Docker and Compose do not restart a container just because it is unhealthy.** They only report it. A restart policy acts when the *process exits*. Orchestrators (Swarm, Kubernetes, ECS) do act on health. Let us see an unhealthy container for real by taking away its dependency, Redis:

```bash run
docker compose up -d --no-deps --scale api=1 api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q api | head -1)")" = healthy ] && break; sleep 1; done
api_status() { docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q api | head -1)"; }
echo "before: api is $(api_status), readyz = $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)"

docker compose stop redis > /dev/null 2>&1
echo "--- redis stopped"
echo "healthz (liveness)  : $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/healthz)   <- still alive: a restart would not help"
echo "readyz (readiness)  : $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)"
curl -s localhost:18080/readyz | jq -c .
for i in $(seq 1 40); do [ "$(api_status)" = unhealthy ] && break; sleep 1; done
echo "docker's view       : api is $(api_status)"
echo "a request that needs redis: $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/hits)"

docker compose start redis > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(api_status)" = healthy ] && break; sleep 1; done
echo "--- redis started again"
echo "docker's view       : api is $(api_status), readyz = $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)"
```
```text
before: api is healthy, readyz = 200
--- redis stopped
healthz (liveness)  : 200   <- still alive: a restart would not help
readyz (readiness)  : 503
{"status":"not ready","problems":{"redis":"ConnectionError"}}
docker's view       : api is unhealthy
a request that needs redis: 500
--- redis started again
docker's view       : api is healthy, readyz = 200
```

Look at the sequence: with Redis gone, **liveness stayed green** (the process is fine, so restarting would only add noise), **readiness turned red** with the reason (`redis: ...`), Docker marked the container `unhealthy`, and the one endpoint that needs Redis answered `500` (which, as in section 8, carries a request id and a traceback in the log). When Redis came back, everything recovered by itself, without a restart. That is the behaviour you want from a well-designed pair of checks.

### 9.4 The same checks in Kubernetes

If you later deploy to Kubernetes, the three checks map directly (you can keep your endpoints and Dockerfile unchanged):

```yaml
containers:
  - name: api
    image: ghcr.io/you/pagebound-api:1.4.2
    startupProbe:   { httpGet: { path: /healthz, port: 8000 }, failureThreshold: 30, periodSeconds: 2 }
    livenessProbe:  { httpGet: { path: /healthz, port: 8000 }, periodSeconds: 10, failureThreshold: 3 }
    readinessProbe: { httpGet: { path: /readyz,  port: 8000 }, periodSeconds: 5,  failureThreshold: 2 }
    lifecycle:
      preStop: { exec: { command: ["sleep", "5"] } }     # give the load balancer a moment to stop sending traffic
  terminationGracePeriodSeconds: 30
```

### 9.5 Graceful shutdown: finish what you started

When the platform stops a container it sends `SIGTERM`. A good service: (1) turns **readiness red** so no new requests arrive, (2) lets requests **already in flight** finish, (3) closes its connections, (4) exits before the kill timeout. Uvicorn does steps 2 to 4 for you; the application's shutdown code does step 1. Test it with a request that is in the middle of its work when the stop arrives:

```bash run
docker compose up -d --no-deps --scale api=1 api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
curl -s -o /dev/null -w "slow request finished with HTTP %{http_code}\n" "localhost:18080/slow?seconds=3" &
sleep 1
docker compose stop -t 10 api > /dev/null 2>&1
wait
docker compose logs api --no-log-prefix 2>/dev/null | grep '^{' | jq -r 'select(.msg == "shutting down" or (.msg == "request" and .route == "/slow")) | "\(.msg) status=\(.status // "-")"' | tail -2
docker compose start api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
```
```text
slow request finished with HTTP 200
request status=200
shutting down status=-
```

The stop arrived while the slow request was running; the request still finished with `200`, **then** the process shut down. Without graceful handling, the client would have seen a dropped connection, and deployments (section 12) would drop requests every time.

### Try it: which check?

For each failure, say whether it should fail liveness, readiness, or neither: (a) the database is unreachable; (b) the process is deadlocked and does not answer at all; (c) the app is warming a large cache for 40 seconds after start; (d) one optional recommendation service, used on only one page, is down.

<details><summary>Answer</summary>

(a) **Readiness** (stop traffic; a restart would not fix the database; keep running so it recovers when the database returns). (b) **Liveness** (only a restart helps; the endpoint cannot answer, so the probe fails by timeout). (c) Neither of the two while it starts: use a **startup** check (or a long `start_period`), then readiness turns green when the cache is warm; do not let liveness kill it during start-up. (d) **Neither**: the service can still serve everything else. Degrade that page gracefully instead of removing the whole instance from rotation.

</details>

### Try it: why not just check everything?

A teammate makes `/healthz` run `SELECT count(*) FROM orders`, ping Redis and call the payment provider, "to be sure". What goes wrong when the payment provider has an outage?

<details><summary>Answer</summary>

The liveness probe fails on every instance, so the platform restarts them all, repeatedly, although they are healthy and the problem is not theirs. Capacity drops to zero, the restarts hammer the database and cache with connection storms, and when the provider returns the system is still recovering from the restart loop. Health checks should check only what is **necessary to serve and under your control**, with short timeouts; external providers belong in metrics and alerts, not in liveness.

</details>

## 10. Metrics and monitoring with Prometheus

### 10.1 Logs tell stories, metrics tell trends

Logs answer "what happened to this request?". They are poor at "how healthy is the service right now?" and "was it slower this week?". **Metrics** are numbers sampled over time, cheap to store and fast to graph. The three types:

| Type | What it is | Example |
|---|---|---|
| **Counter** | a number that only goes up (resets on restart) | `http_requests_total`; you look at its **rate** |
| **Gauge** | a number that goes up and down | requests in flight, queue depth, memory in use |
| **Histogram** | counts of observations in buckets (e.g. latencies), plus a sum and count | `http_request_duration_seconds`; you compute **percentiles** from it |

What to measure? Two checklists:

- **RED** (for services): **R**ate (requests per second), **E**rrors (failed requests per second, or the ratio), **D**uration (latency distribution). Enough to tell if users are happy.
- **USE** (for resources like CPU, disk, queues): **U**tilisation, **S**aturation (queueing or waiting), **E**rrors.

Google's "four golden signals" are latency, traffic, errors and saturation: the union of the two. Our service already exposes RED.

### 10.2 What the service exposes

The `/metrics` endpoint returns plain text in the **Prometheus exposition format**. After the traffic from section 8, look at it:

```bash run
curl -s localhost:18080/metrics | grep -E '^http_requests_total' | grep -v -E '/(metrics|healthz|readyz)' | sort
echo "..."
curl -s localhost:18080/metrics | grep -E 'http_request_duration_seconds_(bucket|sum|count).*route="/slow"' | sed -E 's/,method="GET"//'
```
```text
...
```

Each line is `name{labels} value`. A **label** (`route`, `status`) splits one metric into many *time series*. Read the histogram: `le="0.5"` ("less than or equal 0.5 seconds") counts observations that were at most half a second; buckets are **cumulative**. A request that took 0.6 s appears in the `le="1.0"` bucket and every larger one.

> **The cardinality trap.** Every distinct combination of label values is a separate time series that costs memory and storage. The `route` label holds the route **template** (`/orders/{order_id}`), never the raw path (`/orders/1234`): with raw paths, every order id would create a new series and finally exhaust the monitoring system. The test suite checks this. Never use user ids, e-mail addresses, request ids or full URLs as label values.

### 10.3 Tutorial: run Prometheus

**Prometheus** is a time-series database that **pulls** (scrapes) the `/metrics` endpoint of every target at an interval, stores the values, and answers queries in its language, **PromQL**. Its configuration says what to scrape. Ours finds all replicas of the `api` service through Docker's DNS:

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

rule_files:
  - /etc/prometheus/alerts.yml

scrape_configs:
  - job_name: pagebound
    dns_sd_configs:                 # finds every replica of the "api" service, even after scaling
      - names: [api]
        type: A
        port: 8000
```

Add Prometheus to Compose as an *optional* service (a **profile**, started only when requested, so that the main system stays small):

```diff
# compose.yaml
- volumes:
-   api-data:
+   prometheus:
+     image: prom/prometheus:latest
+     profiles: ["monitoring"]                    # started only with: docker compose --profile monitoring up -d
+     ports:
+       - "127.0.0.1:${PROMETHEUS_PORT:-19090}:9090"
+     volumes:
+       - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
+       - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro
+
+ volumes:
+   api-data:
```

The alert rules file is used in section 10.5; Prometheus needs it to exist now, so create it with the content shown there. Start everything, generate traffic over about a minute (rates need several scrapes), and ask Prometheus which targets it found:

```bash run
cat > monitoring/alerts.yml <<'YAMLEOF'
groups: []
YAMLEOF
docker compose --profile monitoring up -d prometheus 2>&1 | grep -E "Started|Running" | sed -E 's/ +$//' | sort | uniq
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
for round in 1 2 3 4; do ./traffic.sh; curl -s -o /dev/null localhost:18080/boom; sleep 4; done
sleep 8
echo "--- targets Prometheus is scraping:"
curl -s localhost:19090/api/v1/targets | jq -c '.data.activeTargets[] | {job: .labels.job, health}'
```
```text
 Container pbtut-prometheus-1 Started
--- targets Prometheus is scraping:
{"job":"pagebound","health":"up"}
```

(Prometheus discovers the replicas through DNS every few seconds, so there is one target for each API container; scale the service up and a new target appears by itself.) Prometheus has a web UI at `http://localhost:19090` (the *Graph* tab is the place to explore); here we use its HTTP API with `curl` and `jq`, so the results are visible in this text. Run each query and read the answer:

```bash run
q() { curl -s --get localhost:19090/api/v1/query --data-urlencode "query=$1" | jq -c '.data.result | map({metric: (.metric | del(.__name__, .job, .instance)), value: (.value[1] | tonumber | . * 100 | round / 100)}) | sort_by(.metric | tostring)'; }
echo "1. is every target up?   up"
curl -s --get localhost:19090/api/v1/query --data-urlencode 'query=up' | jq -c '[.data.result[].value[1]] | sort'
echo "2. requests so far by status (all API replicas added together):"
q 'sum by (status) (http_requests_total{route!~"/(metrics|healthz|readyz)"})'
echo "3. requests per second over the last minute, by route:"
q 'sum by (route) (rate(http_requests_total{route!~"/(metrics|healthz|readyz)"}[1m])) > 0'
echo "4. the share of requests that fail (status 5xx):"
q 'sum(rate(http_requests_total{status=~"5.."}[1m])) / sum(rate(http_requests_total{route!~"/(metrics|healthz|readyz)"}[1m]))'
echo "5. the 95th percentile latency in seconds, from the histogram buckets:"
q 'histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route!~"/(metrics|healthz|readyz)"}[1m])))'
```
```text
1. is every target up?   up
["1"]
2. requests so far by status (all API replicas added together):
[{"metric":{"status":"200"},"value":28},{"metric":{"status":"201"},"value":80},{"metric":{"status":"404"},"value":12},{"metric":{"status":"500"},"value":4}]
3. requests per second over the last minute, by route:
[{"metric":{"route":"/boom"},"value":0.06},{"metric":{"route":"/orders"},"value":0.83},{"metric":{"route":"/orders/{order_id}"},"value":0.37},{"metric":{"route":"/slow"},"value":0.06}]
4. the share of requests that fail (status 5xx):
[{"metric":{},"value":0.05}]
5. the 95th percentile latency in seconds, from the histogram buckets:
[{"metric":{},"value":0.02}]
```

| PromQL idea | Meaning |
|---|---|
| `metric{label="x"}`, `=~"regex"`, `!~` | select series by labels |
| `rate(counter[1m])` | per-second increase over the last minute; **always use `rate` on counters** (a raw counter is a meaningless ever-growing number) |
| `increase(counter[5m])` | total increase over 5 minutes |
| `sum by (label) (...)` | add series together, keep one label |
| `histogram_quantile(0.95, ...)` | estimate a percentile from histogram buckets |
| `a / b` | arithmetic between series (error ratio) |
| `up` | built-in: 1 if the last scrape worked, 0 if not |

### 10.4 Percentiles, not averages

The average latency hides the worst experiences: if 99 requests take 50 ms and one takes 5 seconds, the average is 100 ms and looks fine, while one user in a hundred waited five seconds. Look at the **95th and 99th percentiles** ("p95, p99": the time that 95% / 99% of requests beat). Histograms make this possible without storing every request, at the price of bucket-sized accuracy, so choose buckets around the latencies you care about.

### 10.5 Alerts

An **alert rule** is a PromQL condition plus a duration. Prometheus evaluates it regularly; when it holds for the `for:` time, the alert fires and is sent to **Alertmanager**, which groups alerts and routes them to e-mail, Slack, or a paging service. Our rules (with short `for:` times so that the tutorial finishes quickly; production values are minutes):

```yaml
# monitoring/alerts.yml
groups:
  - name: pagebound
    rules:
      - alert: InstanceDown
        expr: up{job="pagebound"} == 0
        for: 15s
        labels: {severity: page}
        annotations: {summary: "{{ $labels.instance }} cannot be scraped"}

      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[30s])) / sum(rate(http_requests_total{route!~"/(metrics|healthz|readyz)"}[30s])) > 0.05
        for: 15s
        labels: {severity: page}
        annotations: {summary: "More than 5% of requests are failing"}

      - alert: SlowRequests
        expr: histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route!~"/(metrics|healthz|readyz)"}[1m]))) > 0.5
        for: 2m
        labels: {severity: ticket}
        annotations: {summary: "95th percentile latency is above 500 ms"}
```

Always **check** rule and configuration files before loading them. Prometheus ships a checker, `promtool`:

```bash run
docker compose --profile monitoring up -d --force-recreate prometheus > /dev/null 2>&1
sleep 3
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml 2>&1 | sed 's/^/  /'
```
```text
  Checking /etc/prometheus/prometheus.yml
    SUCCESS: 1 rule files found
   SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
  
  Checking /etc/prometheus/alerts.yml
    SUCCESS: 3 rules found
  
```

Now make the error rate exceed 5% and watch the alert go through its states: `inactive`, then `pending` (the condition holds, but not yet for the `for:` time), then `firing`:

```bash run
alert_state() { curl -s localhost:19090/api/v1/alerts | jq -r '[.data.alerts[] | select(.labels.alertname == "HighErrorRate") | .state] | if length == 0 then "inactive" else .[0] end'; }
until [ "$(alert_state)" = inactive ]; do sleep 2; done      # let the traffic of the previous steps age out of the 30 s window
echo "before the failures : $(alert_state)"
for i in $(seq 1 20); do curl -s -o /dev/null localhost:18080/boom; curl -s -o /dev/null localhost:18080/orders/1; sleep 0.3; done
saw_pending=no
for i in $(seq 1 30); do
  state=$(alert_state)
  [ "$state" = pending ] && saw_pending=yes
  [ "$state" = firing ] && break
  curl -s -o /dev/null localhost:18080/boom; curl -s -o /dev/null localhost:18080/orders/1
  sleep 1
done
echo "went through pending : $saw_pending"
echo "final state          : $(alert_state)"
curl -s localhost:19090/api/v1/alerts | jq -c '.data.alerts[] | select(.labels.alertname == "HighErrorRate") | {alert: .labels.alertname, severity: .labels.severity, summary: .annotations.summary}'
```
```text
before the failures : inactive
went through pending : yes
final state          : firing
{"alert":"HighErrorRate","severity":"page","summary":"More than 5% of requests are failing"}
```

### 10.6 Dashboards, Alertmanager and good alerts

- **Grafana** draws dashboards from Prometheus. Start it like Prometheus (a container, `grafana/grafana`), add Prometheus as a data source (`http://prometheus:9090`) and build panels from the queries above: requests per second, error ratio, p95 latency, instances up. A good first dashboard has exactly those four.
- **Alertmanager** receives firing alerts and handles grouping, silencing and routing to e-mail, Slack or a paging service.
- **Page a human only for what is urgent, user-visible and needs action now** (the site is down, errors above a threshold, the dead-letter queue growing). Everything else is a ticket or a dashboard. Alerts that fire often and need no action train people to ignore alerts. Every alert needs a **runbook**: a page that says what it means and what to do (section 14).
- Alert on **symptoms** (users see errors, latency is high), not on every cause (CPU at 80%).

### 10.7 Service level objectives

An **SLI** (service level indicator) is a measured quality, such as "the share of requests answered successfully in under 500 ms". An **SLO** (objective) is the target for it, such as "99.9% over 30 days". The gap between the target and perfection is the **error budget**: 99.9% over 30 days allows 0.1% failures, about **43 minutes of total downtime** or the equivalent in failed requests. While the budget lasts, you can ship quickly; when it is spent, you slow down and fix reliability. It turns the argument "is it reliable enough?" into a number. Prometheus gives you the SLI directly: `1 - (sum(rate(...5xx...)) / sum(rate(...all...)))`.

```bash run
python3 - <<'PYEOF'
for slo in (99.0, 99.9, 99.99):
    budget_minutes = 30 * 24 * 60 * (100 - slo) / 100
    print(f"SLO {slo:>5}% over 30 days -> error budget {budget_minutes:7.1f} minutes of full downtime")
PYEOF
```
```text
SLO  99.0% over 30 days -> error budget   432.0 minutes of full downtime
SLO  99.9% over 30 days -> error budget    43.2 minutes of full downtime
SLO 99.99% over 30 days -> error budget     4.3 minutes of full downtime
```

### Try it: which metric type?

Choose counter, gauge or histogram: (a) number of orders created; (b) number of jobs waiting in the queue; (c) time to render a report; (d) bytes sent to clients.

<details><summary>Answer</summary>

(a) Counter (it only grows; look at its `rate`). (b) Gauge (rises and falls). (c) Histogram (you want percentiles of a duration). (d) Counter (monotonic total; its rate is the bandwidth).

</details>

### Try it: why is the alert silent?

You wrote an alert `rate(http_requests_total{status="500"}[1m]) > 0.5`, a test sent 100 failing requests in a second, and nothing fired. Give three possible reasons.

<details><summary>Answer</summary>

(1) The `for:` duration was longer than the burst, so the condition did not hold for long enough (it stays `pending`). (2) The rate is computed over the last minute and per series; a 1-second burst spread over `[1m]` averages to about 1.7/s per series if you sum them, but per-replica series can each stay below 0.5 (use `sum(rate(...))`). (3) Prometheus scrapes every 5 to 15 seconds and needs at least two points inside the range; the burst may fall between scrapes, and the first evaluation after a restart has no history. Test alerts with sustained load, not a spike.

</details>


## 11. Continuous integration with GitHub Actions

### 11.1 What CI is for

**Continuous integration (CI)** means that every change to the code is automatically built and tested on a clean machine, within minutes, before it is merged. It answers three questions that "it works on my laptop" cannot: *does it work on a machine that is not mine?*, *did this change break something else?*, and *can we build the thing that we are going to ship?* **Continuous delivery** extends the idea: a change that passes can be deployed (by a button or automatically). CI is a safety net that also makes people braver: small changes, merged often, with the machine watching.

**GitHub Actions** is GitHub's built-in CI/CD service (alternatives: GitLab CI, Jenkins, CircleCI, Buildkite). You describe what to run in a YAML file inside the repository, and GitHub runs it on its virtual machines. It is free for public repositories and has a free allowance for private ones.

### 11.2 The vocabulary

| Word | Meaning |
|---|---|
| **Workflow** | one automated process, defined by a YAML file in `.github/workflows/` |
| **Event / trigger** | what starts it: `push`, `pull_request`, a version tag, a schedule, a manual button (`workflow_dispatch`) |
| **Job** | a group of steps that runs on one machine; jobs run in parallel unless one `needs` another |
| **Runner** | the machine that executes a job (`ubuntu-latest` is a fresh virtual machine, thrown away afterwards) |
| **Step** | one command (`run:`) or one reusable **action** (`uses:`) |
| **Action** | a packaged step written by someone else (`actions/checkout@v4` downloads your code) |
| **Secret** | an encrypted value you store in the repository settings; used as `${{ secrets.NAME }}` |
| **Matrix** | run the same job with several values (for example two Python versions) |
| **Artifact / cache** | files kept between jobs / between runs (the pip cache) |

### 11.3 CI is just commands: put them in a Makefile

The most useful habit: **the CI configuration should contain almost no logic**. Put the commands in a script or a `Makefile`, run the same thing on your laptop, and let CI call it. Then "it fails in CI" can be reproduced locally with one command, and the pipeline is easy to move to another service.

```makefile
# Makefile
.PHONY: test typecheck workflow-check build ci

PYTHON  ?= python
VERSION ?= dev

test:
	PYTHONPATH=. $(PYTHON) -m pytest -q -p no:cacheprovider -W ignore tests

typecheck:
	$(PYTHON) -m mypy app --ignore-missing-imports

workflow-check:
	$(PYTHON) check_workflow.py .github/workflows/ci.yml

build:
	docker build -q -t pagebound-api:$(VERSION) --build-arg APP_VERSION=$(VERSION) .

ci: typecheck test workflow-check build
	@echo "CI passed for version $(VERSION)"
```

(A Makefile needs real **tab** characters before the commands. `make` is available on Linux and macOS; on Windows use WSL.) Run the whole pipeline locally. This is what the machine in the cloud will do:

```bash run
make typecheck test 2>&1 | sed -E 's/ in [0-9.]+s//'
```
```text
python -m mypy app --ignore-missing-imports
Success: no issues found in 4 source files
PYTHONPATH=. python -m pytest -q -p no:cacheprovider -W ignore tests
......                                                                   [100%]
6 passed
```

Type checking (mypy) and the tests passed. (`make ci` runs these two plus the workflow lint of section 11.5 and the Docker build; we run it in full once those files exist, below.) If any step fails, `make` stops and returns an error, and that is exactly what turns a CI job red.

### 11.4 The workflow file

```yaml
# .github/workflows/ci.yml
name: ci

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install dependencies
        run: pip install -r requirements.txt pytest httpx mypy
      - name: Type check
        run: make typecheck
      - name: Tests
        run: make test

  image:
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Log in to GitHub Container Registry
        if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build (and push on main or on a version tag)
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v') }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          build-args: APP_VERSION=${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Read it in layers:

- **`on:`** the triggers: pushes to `main`, version tags such as `v1.2.0`, every pull request, and a manual button.
- **`permissions: contents: read`** at the top: the automatic token can only read the repository by default. Each job asks for more only if it needs it (`packages: write` for pushing images). This is *least privilege* (swe.07) applied to CI.
- **`concurrency`**: when you push twice quickly, the older run is cancelled instead of wasting time.
- **Job `test`**: runs on a fresh Ubuntu machine, once for each Python version in the **matrix** (3.13 and 3.14), installs dependencies (with pip's cache), then runs `make typecheck` and `make test`. `timeout-minutes` stops a hung job.
- **Job `image`**: `needs: test`, so it runs only if the tests passed. It builds the Docker image with BuildKit and **pushes it to the GitHub Container Registry only on `main` or a version tag** (`push: ${{ ... }}`), tagged with the commit SHA. On a pull request it only builds, to prove the Dockerfile still works. It authenticates with the automatic `GITHUB_TOKEN`, so no password is stored anywhere.
- **Action versions** like `actions/checkout@v4` are *moving* tags that the action's author controls. Official actions (`actions/*`, `docker/*`) are commonly used with a major tag; for third-party actions pin a full commit SHA (`uses: someone/action@8f3c...`), because a compromised tag would otherwise run attacker code with your secrets (this attack has happened). Dependabot (below) keeps pinned versions fresh.

### 11.5 Lint your CI before GitHub does

A CI file that is wrong tells you only after a push, in a browser tab. A small checker finds the common mistakes locally. This one uses the PyYAML you already have, and it knows a famous YAML trap: YAML 1.1 reads the key `on` as the boolean `True`, so the trigger section of a workflow arrives as `workflow[True]`:

```python
# check_workflow.py
"""A small linter for GitHub Actions workflow files. usage: python check_workflow.py .github/workflows/ci.yml"""
import re
import sys

import yaml

MOVING_REFS = {"main", "master", "latest", "HEAD"}


def check(workflow: dict) -> list[tuple[str, str]]:
    problems = []
    triggers = workflow.get("on", workflow.get(True))        # YAML 1.1 reads the key `on` as the boolean True!
    if not triggers:
        problems.append(("error", "no trigger: add an `on:` section"))
    if isinstance(triggers, dict) and "pull_request_target" in triggers:
        problems.append(("error", "pull_request_target runs with secrets on code from forks: avoid it"))
    if "permissions" not in workflow:
        problems.append(("warning", "no top-level `permissions:`; the default token may be too powerful"))
    jobs = workflow.get("jobs") or {}
    if not jobs:
        problems.append(("error", "no jobs"))
    for name, job in jobs.items():
        if "runs-on" not in job:
            problems.append(("error", f"job {name!r} has no runs-on"))
        if "timeout-minutes" not in job:
            problems.append(("warning", f"job {name!r} has no timeout-minutes; a hung job runs for 6 hours"))
        for need in ([job["needs"]] if isinstance(job.get("needs"), str) else job.get("needs", [])):
            if need not in jobs:
                problems.append(("error", f"job {name!r} needs {need!r}, which does not exist"))
        for i, step in enumerate(job.get("steps") or [], 1):
            uses, run = step.get("uses"), step.get("run", "")
            if uses and "@" not in uses and not uses.startswith("./"):
                problems.append(("error", f"{name} step {i}: {uses!r} has no version after @"))
            elif uses and uses.split("@", 1)[1] in MOVING_REFS:
                problems.append(("error", f"{name} step {i}: {uses!r} follows a moving branch; pin a version or a commit SHA"))
            elif uses and not uses.startswith(("actions/", "docker/")) and not re.fullmatch(r"[0-9a-f]{40}", uses.split("@", 1)[1]):
                problems.append(("warning", f"{name} step {i}: third-party action {uses!r} should be pinned to a full commit SHA"))
            if re.search(r"\$\{\{\s*secrets\.", run):
                problems.append(("error", f"{name} step {i}: a secret is pasted into a `run:` script; pass it through `env:`"))
    return problems


def main(path: str) -> int:
    try:
        with open(path) as f:
            workflow = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f"ERROR   not valid YAML: {str(exc).splitlines()[0]} ({getattr(exc, 'problem_mark', None) and 'line ' + str(exc.problem_mark.line + 1)})")
        return 1
    problems = check(workflow)
    for level, text in problems:
        print(f"{level.upper():7} {text}")
    errors = sum(level == "error" for level, _ in problems)
    print(f"{path}: {errors} error(s), {len(problems) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

```bash run
python check_workflow.py .github/workflows/ci.yml
cat > bad.yml <<'YAMLEOF'
name: bad
on:
  pull_request_target:
jobs:
  build:
    needs: test
    steps:
      - uses: actions/checkout
      - uses: someone/deploy-action@main
      - run: |
          curl -H "token: ${{ secrets.DEPLOY_KEY }}" https://example.com
YAMLEOF
echo "--- a deliberately bad workflow:"
python check_workflow.py bad.yml || true
printf 'name: broken\njobs:\n  a:\n    steps:\n      - run: echo hi: there\n' > broken.yml
echo "--- a workflow that is not even valid YAML:"
python check_workflow.py broken.yml || true
```
```text
.github/workflows/ci.yml: 0 error(s), 0 warning(s)
--- a deliberately bad workflow:
ERROR   pull_request_target runs with secrets on code from forks: avoid it
WARNING no top-level `permissions:`; the default token may be too powerful
ERROR   job 'build' has no runs-on
WARNING job 'build' has no timeout-minutes; a hung job runs for 6 hours
ERROR   job 'build' needs 'test', which does not exist
ERROR   build step 1: 'actions/checkout' has no version after @
ERROR   build step 2: 'someone/deploy-action@main' follows a moving branch; pin a version or a commit SHA
ERROR   build step 3: a secret is pasted into a `run:` script; pass it through `env:`
bad.yml: 6 error(s), 2 warning(s)
--- a workflow that is not even valid YAML:
ERROR   not valid YAML: mapping values are not allowed here (line 5)
```

Now the whole pipeline in one command, as the cloud machine will run it:

```bash run
make ci VERSION=1.0.0 2>&1 | sed -E 's/ in [0-9.]+s//; s/sha256:[0-9a-f]+/sha256:.../'
```
```text
python -m mypy app --ignore-missing-imports
Success: no issues found in 4 source files
PYTHONPATH=. python -m pytest -q -p no:cacheprovider -W ignore tests
......                                                                   [100%]
6 passed
python check_workflow.py .github/workflows/ci.yml
.github/workflows/ci.yml: 0 error(s), 0 warning(s)
docker build -q -t pagebound-api:1.0.0 --build-arg APP_VERSION=1.0.0 .
sha256:...
CI passed for version 1.0.0
```

The real-world tool for this is **actionlint** (`docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:latest`), which knows the whole workflow syntax; our checker shows the idea and a few security rules that matter: no `pull_request_target` (it runs with secrets on code from forks), pinned actions, no secrets pasted into scripts (where a shell could print them; pass them through `env:`), job timeouts.

### 11.6 Tutorial: your first green and red build on GitHub

> **Try it on your machine** (needs a **personal** GitHub account and a new repository; the screens are GitHub's, so no output is shown).
>
> ```bash
> git init -b main                       # inside the project folder; skip if it is already a git repository
> git add . && git commit -m "Pagebound service with Docker and CI"
> git remote add origin git@github.com:YOUR_USER/pagebound.git      # create the empty repository on github.com first
> git push -u origin main
> ```
>
> 1. Open the repository on github.com and click the **Actions** tab. The `ci` workflow is running: yellow dot while running, green tick when it passes. Click the run to see each job and each step with its log output.
> 2. **Break it on purpose.** Change an assertion in `tests/test_app.py` (for example `== 201` to `== 200`), commit on a new branch, push, and open a **pull request**. The check shows a red cross and the failing step's log shows the pytest output. GitHub can block merging until checks pass: *Settings, Branches, add a rule for `main`, tick "Require status checks to pass before merging"* and pick `test`.
> 3. Fix the test, push again, and watch the check turn green. This red-green loop is the daily rhythm of CI.
> 4. Add a secret under *Settings, Secrets and variables, Actions* and use it through `env:` in a step. Look at the log: GitHub replaces the value with `***`.
> 5. Create a version tag (`git tag v0.1.0 && git push --tags`). The `image` job pushes the image to `ghcr.io/YOUR_USER/pagebound`, visible under the repository's *Packages*.

### 11.7 Habits around CI

- **Keep CI fast** (under 10 minutes): cache dependencies, run the quick tests first, run slow ones in a separate job. A slow pipeline gets bypassed.
- **Treat a red `main` as an emergency** (stop merging, fix or revert), and never merge on red.
- **Flaky tests** (pass and fail randomly) destroy trust in CI: fix or quarantine them at once (core.19).
- **Secrets**: use the platform's secret store, never print them, and remember that workflows triggered by pull requests from **forks** do not receive secrets (by design).
- **Dependabot** opens pull requests that update your dependencies, base images and actions (`.github/dependabot.yml`), so security fixes arrive as small, tested changes:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule: {interval: weekly}
  - package-ecosystem: docker
    directory: "/"
    schedule: {interval: weekly}
  - package-ecosystem: github-actions
    directory: "/"
    schedule: {interval: weekly}
```

- **Pre-commit hooks** (`pre-commit` tool) run formatters and linters on your machine before each commit, catching problems even earlier than CI.
- Next steps in a mature pipeline: security scanning of dependencies and images (`pip-audit`, `trivy`), deploying to staging automatically, and a manually approved deployment to production (GitHub *Environments* with required reviewers).

### Try it: what could go wrong?

A workflow does `run: echo "Deploying with ${{ secrets.SSH_KEY }}"`. Name the problem, and what a pull request from a stranger's fork could do to a workflow that uses `pull_request_target` and checks out the pull request's code.

<details><summary>Answer</summary>

Pasting the secret into the script means it is expanded into the shell command (visible in logs in edge cases, in process listings, and in any step that fails with a trace); pass secrets through `env:` and refer to the environment variable. GitHub masks exact secret values in logs but cannot mask transformed ones (base64, split in two). With `pull_request_target`, the workflow runs with the base repository's secrets and write token; if it then checks out and runs the code of the pull request, a stranger can run arbitrary code with your secrets. Use `pull_request` (no secrets) for untrusted code.

</details>

### Try it: make it reproducible

Your teammate says "the tests pass for me but fail in CI". List four differences between your machine and the runner that commonly explain it, and the habit that removes most of them.

<details><summary>Answer</summary>

(1) Different Python or dependency versions (unpinned requirements). (2) Files that exist locally but are ignored by git (`.env`, test data, a database). (3) Environment variables and secrets only set on your machine. (4) Test order, time zones, locale or network access (a test calling a real service). (5) State left over from earlier runs on your machine. The habit: pin dependencies, run the same `make ci` command locally and in CI, and run the tests in a clean checkout (or a container) occasionally.

</details>

## 12. Deploying and rolling back

This section delivers the second outcome of the chapter: **roll back a bad deployment.**

### 12.1 Build, release, deploy

| Step | What | Result |
|---|---|---|
| **Build** | turn a commit into an artifact | an image, tagged `1.1.0` (and the git SHA) |
| **Release** | combine the artifact with configuration | "version 1.1.0 for production" |
| **Deploy** | make the running system use the release | containers running 1.1.0 |
| **Rollback** | deploy the previous release again | containers running 1.0.0 |

The reason rollbacks can be quick and safe is that **an image tag is immutable**: `pagebound-api:1.0.0` is exactly the code that ran yesterday, with its dependencies, ready to start. A rollback is *not* "rebuild the old code" (which can behave differently: a dependency changed, a base image moved); it is "start the old image". This is why deployments use version tags, never `latest`, and why registries keep the last several versions.

### 12.2 Deployment strategies

| Strategy | How | Downtime | Rollback | Needs |
|---|---|---|---|---|
| **Recreate** | stop the old, start the new | yes, a short gap | redeploy the old | nothing special |
| **Rolling** | replace instances one at a time, waiting for readiness | none, if more than one instance | stop and roll the other way | several instances, working readiness checks |
| **Blue/green** | run the new version beside the old; switch the proxy; keep the old running | none | switch back (seconds) | double capacity during the switch |
| **Canary** | send a small share (1 to 5%) to the new version, watch the metrics, then increase | none | send 0% to it | traffic splitting, good metrics |
| **Feature flag** | ship code switched off; turn it on later (and off again) | none | flip the flag | flag system (section 3.6) |

The right choice depends on your size. A single server with Compose does *recreate*, perhaps with a second copy for *rolling*. Kubernetes and managed platforms do rolling, blue/green and canary for you; what they need from you is exactly what this chapter builds: **readiness checks that tell the truth**, **graceful shutdown**, and **metrics that show whether the new version is worse**.

### 12.3 Tutorial: a deployment script with automatic rollback

A good deployment does five things: (1) records what is running now, (2) starts the new version, (3) **waits until it is healthy**, (4) **verifies** that it really serves the new version, and (5) if anything fails, **goes back by itself** and says so loudly. Compose's `up --wait` does the waiting for us (it returns an error if a container does not become healthy within the timeout). Here is the script:

```bash
# deploy.sh
#!/usr/bin/env bash
# Deploy one version of the API; roll back automatically if it does not become healthy.
# usage: ./deploy.sh 1.1.0
set -uo pipefail

NEW="${1:?usage: ./deploy.sh <version>}"
PORT="${PUBLIC_PORT:-18080}"
STATE_FILE=".current-version"
PREVIOUS="$(cat "$STATE_FILE" 2>/dev/null || true)"
LOG="$(mktemp)"

served_version() {                       # ask the running service which version it reports
    curl -fsS --max-time 5 "http://127.0.0.1:${PORT}/" | python3 -c 'import sys, json; print(json.load(sys.stdin)["version"])'
}

echo "==> deploying ${NEW} (currently running: ${PREVIOUS:-nothing})"
export APP_VERSION="$NEW"

# images are immutable: an existing tag is reused as it is (this is what makes a rollback fast and exact)
if docker image inspect "pagebound-api:${NEW}" > /dev/null 2>&1; then
    echo "==> image pagebound-api:${NEW} already exists; using it"
else
    echo "==> building pagebound-api:${NEW}"
    docker compose build api > "$LOG" 2>&1 || { echo "==> BUILD FAILED"; tail -n 3 "$LOG" | sed 's/^/    /'; exit 1; }
fi

# --wait: return only when the containers are running and healthy (or fail after the timeout)
if docker compose up -d --wait --wait-timeout 40 api nginx > "$LOG" 2>&1 \
   && curl -fsS --max-time 5 "http://127.0.0.1:${PORT}/readyz" > /dev/null \
   && [ "$(served_version)" = "$NEW" ]; then
    echo "$NEW" > "$STATE_FILE"
    echo "==> ${NEW} is live and healthy"
    exit 0
fi

echo "==> ${NEW} FAILED its health check; last lines of the deploy log:"
tail -n 2 "$LOG" | sed 's/^/    /'
echo "==> last log lines of the failed container (captured BEFORE the rollback removes it):"
docker compose logs --no-log-prefix --tail 3 api 2>/dev/null | cut -c1-150 | sed 's/^/    /'
if [ -z "$PREVIOUS" ]; then
    echo "==> nothing to roll back to"
    exit 1
fi
echo "==> rolling back to ${PREVIOUS}"
export APP_VERSION="$PREVIOUS"
if docker compose up -d --wait --wait-timeout 40 api nginx > "$LOG" 2>&1; then
    echo "==> rolled back: the service is serving version $(served_version)"
    exit 1                                # still a failed deployment: the pipeline must not report success
fi
echo "==> ROLLBACK FAILED: page a human"
exit 2
```

First deploy version 1.0.0 to a clean state. The script builds the image if the tag does not exist yet, starts the services, waits for health, and checks which version answers:

```bash run
chmod +x deploy.sh
docker compose up -d --no-deps --scale api=1 api > /dev/null 2>&1
./deploy.sh 1.0.0
```
```text
==> deploying 1.0.0 (currently running: nothing)
==> image pagebound-api:1.0.0 already exists; using it
==> 1.0.0 is live and healthy
```

#### A good release, and the cost of "recreate"

Make a real change: a new field in the root response. Meanwhile we send a request every 100 milliseconds in the background, to measure what users experience during the switch:

```diff
# app/main.py
-         return {"service": "pagebound", "version": settings.version, "env": settings.env, "instance": instance}
+         return {"service": "pagebound", "version": settings.version, "env": settings.env, "instance": instance, "feature": "orders-v2"}
```

```bash run
( while true; do curl -s -o /dev/null -w '%{http_code}\n' --max-time 1 localhost:18080/; sleep 0.1; done > codes.txt ) &
loop=$!
sleep 1
./deploy.sh 1.1.0
sleep 1
kill $loop; wait $loop 2>/dev/null
echo "requests were sent during the deployment: $([ "$(wc -l < codes.txt)" -gt 20 ] && echo yes || echo no)"
echo "some of them failed (recreate = gap): $([ "$(grep -vc '^200$' codes.txt)" -gt 0 ] && echo yes || echo no)"
echo "the new version answers now          : $(curl -s localhost:18080/ | jq -c '{version, feature}')"
```
```text
==> deploying 1.1.0 (currently running: 1.0.0)
==> image pagebound-api:1.1.0 already exists; using it
==> 1.1.0 is live and healthy
requests were sent during the deployment: yes
some of them failed (recreate = gap): yes
the new version answers now          : {"version":"1.1.0","feature":"orders-v2"}
```

The new version is live, and the numbers show the price of the simplest strategy: between "old container stopped" and "new container ready", Nginx had nothing to talk to and returned errors. For a small internal tool that may be fine. When it is not, you run **two or more instances and replace them one at a time** (rolling), or run the new version next to the old and switch (blue/green); orchestrators do this for you. The health checks are what make those strategies safe.

#### A bad release, and the automatic rollback

Now the scenario that matters. A developer adds a new required setting to the configuration and forgets that production does not have it. The tests pass (they build their own settings), the image builds, and the container crashes at start-up, because our `Settings` object refuses to start with an incomplete configuration (section 3):

```diff
# app/config.py
-         problems = []
+         problems = []
+         if not e.get("PAYMENTS_API_KEY"):
+             problems.append("PAYMENTS_API_KEY is required")
```

```bash run
./deploy.sh 2.0.0 ; echo "deploy script exit code: $?"
echo "--- what is serving traffic now?"
curl -s localhost:18080/ | jq -c '{version, feature}'
docker compose ps api nginx --format '{{.Service}} {{.Status}}' | sed -E 's/Up (About a|[0-9]+) (second|minute|hour)s?/Up N time/'
```
```text
==> deploying 2.0.0 (currently running: 1.1.0)
==> image pagebound-api:2.0.0 already exists; using it
==> 2.0.0 FAILED its health check; last lines of the deploy log:
     Container pbtut-api-1 Error dependency api failed to start
    dependency failed to start: container pbtut-api-1 is unhealthy
==> last log lines of the failed container (captured BEFORE the rollback removes it):
        raise ConfigError("; ".join(problems))                  # refuse to start with a bad configuration
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    app.config.ConfigError: PAYMENTS_API_KEY is required
==> rolling back to 1.1.0
==> rolled back: the service is serving version 1.1.0
deploy script exit code: 1
--- what is serving traffic now?
{"version":"1.1.0","feature":"orders-v2"}
api Up N time (healthy)
nginx Up N time
```

Follow the script's story. `up --wait` returned an error because the new container never became healthy (it crashed at start-up). The script reported the failure, **printed the last log lines of the failed container** (before the rollback removes it: that is where the cause is, here `PAYMENTS_API_KEY is required`), **started the previous release again** from the image it already had, and confirmed that version 1.1.0 is serving. The deployment failed (non-zero exit code, so the pipeline turns red) but **users saw the bad version only for the start-up time**, and the failure was caught by a health check, not by a customer. Capturing the evidence before cleaning up is a habit worth copying: a rollback that destroys the logs of the failure makes the investigation harder.

Now fix the code (here we revert the bad change) and deploy a corrected version, **2.0.1**:

```diff
# app/config.py
-         problems = []
-         if not e.get("PAYMENTS_API_KEY"):
-             problems.append("PAYMENTS_API_KEY is required")
+         problems = []
```

#### A manual rollback to an older version

Sometimes a release is "healthy" and still wrong (a business bug that no health check can see: wrong prices, a broken page). Then a human decides to go back. Because images are immutable and still on the machine, it is the same script with the old version number, and no rebuild:

```bash run
docker images pagebound-api --format '{{.Tag}}' | sort | tr '\n' ' '; echo
echo "--- roll back by hand to 1.0.0 (an older image: no rebuild)"
./deploy.sh 1.0.0
curl -s localhost:18080/ | jq -c '{version, feature}'
```
```text
1.0.0 1.1.0 2.0.0 
--- roll back by hand to 1.0.0 (an older image: no rebuild)
==> deploying 1.0.0 (currently running: 1.1.0)
==> image pagebound-api:1.0.0 already exists; using it
==> 1.0.0 is live and healthy
{"version":"1.0.0","feature":null}
```

The reply no longer has a `feature` field, because it is the **old image**, built from the old code. That is the proof that a rollback restores the exact earlier release.

### 12.4 Rollback and the database

Code rollback is easy because code is stateless. **The database is not.** If version 1.1.0 changed the schema and wrote data in a new shape, going back to 1.0.0's code means old code meeting new data. The safe way to change a schema is the **expand and contract** pattern, in separate releases:

1. **Expand**: make a change that old code tolerates, usually *adding* a nullable column or a new table. Deploy it. Old code ignores the new column.
2. **Migrate the code**: deploy code that writes both the old and new shapes, and reads the new. Back-fill existing rows.
3. **Contract**: once nobody can need the old shape (and you can no longer roll back that far), remove it in a later release.

```python run
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT NOT NULL, quantity INTEGER NOT NULL);"
                 "INSERT INTO orders (item, quantity) VALUES ('pen', 3);")
old_code_read = "SELECT id, item, quantity FROM orders"                     # what version 1.0.0 runs
old_code_write = "INSERT INTO orders (item, quantity) VALUES (?, ?)"

db.execute("ALTER TABLE orders ADD COLUMN note TEXT")                       # 1.1.0's migration: only ADDS a column
print("expand (add a nullable column): version 1.0.0 still works ->", db.execute(old_code_read).fetchall(),
      "| insert ok:", db.execute(old_code_write, ("ink", 1)).rowcount == 1)

db.execute("ALTER TABLE orders RENAME COLUMN quantity TO qty")              # a destructive migration
try:
    db.execute(old_code_read)
except sqlite3.OperationalError as exc:
    print("rename a column: version 1.0.0 breaks ->", exc)
```
```text
expand (add a nullable column): version 1.0.0 still works -> [(1, 'pen', 3)] | insert ok: True
rename a column: version 1.0.0 breaks -> no such column: quantity
```

Rules that follow: never rename, drop or change the type of a column in the same release that stops using it; run migrations as a separate, earlier step than the code that needs them (a one-off `docker compose run --rm api <migrate command>`, the "admin tasks" factor of section 1.3); take a **backup immediately before** any risky migration (section 13); and know in advance whether a rollback is possible for this release. If it is not (data was transformed one way), say so in the release plan and prefer **rolling forward** (a fast fix and redeploy) over a rollback that corrupts data.

### 12.5 Deployment hygiene

- **Verify after deploying**: the script checked readiness and the version; add a *smoke test* of one real user flow, and watch the error rate and latency dashboards (section 10) for a few minutes. Alerts firing in the first minutes after a deployment usually mean the deployment caused them.
- **Deploy small and often.** A change of 20 lines is easy to understand and to roll back; a change of 2,000 is a gamble.
- **Keep the last several images** (and their configuration) available; prune old ones by age, not by hand.
- **One command, same every time**: no editing files on the server. If a person types steps from memory, a deployment will eventually go wrong.
- **Log what was deployed, when, by whom** (the script's output, the CI run). When something breaks, the first question is "what changed?".
- **Communicate**: tell the team before and after; avoid risky deployments when nobody can respond (the old advice about Friday afternoons is about people, not technology).
- **Roll back first, investigate second.** If a release is clearly bad, restoring service comes before understanding.

### 12.6 From your laptop to a server

> **Try it on your machine** (needs a small cloud server, for example a Linux virtual machine from any provider, and a domain name; not run here). The steps map directly to what you did locally:
>
> ```bash
> ssh youruser@SERVER_IP                                  # log in with an SSH key, not a password
> sudo ufw default deny incoming && sudo ufw allow 22,80,443/tcp && sudo ufw enable   # firewall: only SSH and web
> # install Docker Engine from the official guide, then:
> mkdir -p ~/pagebound && cd ~/pagebound
> # copy compose.yaml, nginx/, monitoring/ and a .env (chmod 600) to this folder, for example with scp
> docker login ghcr.io                                    # so the server can pull your private image
> APP_VERSION=1.0.0 docker compose pull && docker compose up -d --wait
> ```
>
> Point a DNS `A` record for your domain at the server's IP, get a real certificate with `certbot` (section 7.6), and from now on let CI (or a small script like `deploy.sh`) run `docker compose pull && docker compose up -d --wait` over SSH. Two warnings: Docker publishes ports **around** simple `ufw` rules, so bind internal services to `127.0.0.1` as in the Compose file; and never expose the Docker socket or databases to the internet.

### Try it: why did the rollback work?

List the properties of the system that made the automatic rollback in 12.3 possible. Which one would be missing if the script ran `docker compose build` for the old version?

<details><summary>Answer</summary>

(1) A **health check** that fails for a broken release, plus `--wait` so that the script notices. (2) **Immutable, versioned images** (the old version still exists and starts in seconds). (3) The script **records the previous version**. (4) A **post-deploy verification** (right version, readiness green). (5) **Configuration validated at start-up**, so a bad configuration fails loudly instead of limping. A rebuild of the old version would lose (2): it would rebuild from whatever the code, base image and dependencies are *today*, which may not be what ran before.

</details>

### Try it: roll forward or back?

A release changed prices to a new table and migrated the data in place; 20 minutes later users report wrong totals. The database has taken 300 new orders since the deployment. What are the risks of rolling back, and what do you do?

<details><summary>Answer</summary>

Rolling back the code to a version that reads the old price table would show old (or missing) prices for data now living in the new table, and it would write 300 new-style orders it cannot interpret: the rollback itself corrupts data. First stop the damage (feature flag off, maintenance page, or a fast fix), restore from a backup only if the data is truly damaged and you accept losing the 20 minutes of orders, and otherwise **roll forward** with a fix that handles both shapes. The lesson is expand and contract (section 12.4): this release should never have transformed data in place.

</details>

## 13. Backups and restore drills

### 13.1 The only backup that counts is one you have restored

Data is lost by hardware failure, by someone running `DELETE` without `WHERE`, by a bug that quietly corrupts rows for a week, by ransomware, by an accidental `docker compose down -v`. Remember three ideas:

- **Backups are not replicas.** A replica (a second database that copies the first in real time) protects against a dead machine, but it copies your mistakes and deletions within a second. A backup is a *separate, older* copy.
- **A backup you have never restored is a hope, not a backup.** Corrupt files, missing tables, lost encryption keys and wrong versions are discovered only by restoring. A scheduled **restore drill** is what turns hope into knowledge.
- **The 3-2-1 rule:** keep **3** copies of the data, on **2** different kinds of storage, with **1** copy **off-site** (another building or provider), and protect backups from the same mistakes (a separate account or write-once storage).

Two numbers define what you need:

| Term | Question | Example |
|---|---|---|
| **RPO** (recovery point objective) | how much recent data can we afford to lose? | 24 hours (a nightly backup), or 5 minutes (continuous log shipping) |
| **RTO** (recovery time objective) | how long may recovery take? | 4 hours, or 15 minutes |

Back up what cannot be rebuilt: **databases**, **uploaded files**, and the **configuration needed to rebuild** (infrastructure files, a safe copy of the secrets in your secret manager). Do not back up what can be regenerated (caches, built images, `node_modules`). **Encrypt** backups (they contain all your data), keep them for a **retention** period that matches your needs and any legal rules, and remember that "delete my data" requests apply to backups too.

### 13.2 Tutorial: SQLite backup, disaster and restore

Our service stores its data in a SQLite file in a Docker volume. **Copying a SQLite file while the application is writing can produce a corrupt copy** (the file is changed in the middle of your copy). Use SQLite's own **online backup API**, which takes a consistent snapshot. The script also checks the copy (`PRAGMA integrity_check`), stores a checksum, and keeps only the newest N backups:

```python
# backup.py
"""Online backup of a SQLite database.   usage: python backup.py DB_FILE BACKUP_DIR [KEEP]"""
import hashlib
import sqlite3
import sys
import time
from pathlib import Path


def backup(db_file, backup_dir, keep=7, now=time.time):
    db_file, backup_dir = Path(db_file), Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"{db_file.stem}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(now()))}.db"

    source = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    copy = sqlite3.connect(target)
    with copy:
        source.backup(copy)                              # a consistent snapshot, even while the application keeps writing
    source.close()

    verdict = copy.execute("PRAGMA integrity_check").fetchone()[0]
    copy.close()
    if verdict != "ok":                                  # never keep a backup you already know is bad
        target.unlink()
        raise SystemExit(f"backup FAILED the integrity check: {verdict}")

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    Path(f"{target}.sha256").write_text(f"{digest}  {target.name}\n")

    for old in sorted(backup_dir.glob(f"{db_file.stem}-*.db"))[:-keep]:       # retention: keep the newest `keep`
        old.unlink()
        Path(f"{old}.sha256").unlink(missing_ok=True)
    return target, digest


if __name__ == "__main__":
    path, digest = backup(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 7)
    print(f"backup ok: {path.name} sha256={digest[:12]}...")
```

And the drill: a script that takes a backup file and **proves** it can be used: the checksum matches, a restore into a fresh empty database works, the database passes its integrity check, and the data is really there:

```python
# restore_drill.py
"""Prove that a backup restores.   usage: python restore_drill.py BACKUP_FILE [MIN_ORDERS]"""
import hashlib
import sqlite3
import sys
import tempfile
import time
from pathlib import Path


def drill(backup_file, min_orders=1):
    backup_file, started, steps = Path(backup_file), time.perf_counter(), []

    expected = Path(f"{backup_file}.sha256").read_text().split()[0]          # 1. is the file the one we wrote?
    actual = hashlib.sha256(backup_file.read_bytes()).hexdigest()
    steps.append(("checksum matches", actual == expected))

    with tempfile.TemporaryDirectory() as tmp:                               # 2. restore into a fresh, empty place
        restored = Path(tmp) / "restored.db"
        source, target = sqlite3.connect(backup_file), sqlite3.connect(restored)
        with target:
            source.backup(target)
        source.close()

        steps.append(("integrity check ok", target.execute("PRAGMA integrity_check").fetchone()[0] == "ok"))   # 3. is it sound?
        tables = {row[0] for row in target.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        steps.append(("table 'orders' exists", "orders" in tables))
        count = target.execute("SELECT count(*) FROM orders").fetchone()[0] if "orders" in tables else 0
        steps.append((f"at least {min_orders} order(s) present", count >= min_orders))   # 4. is the DATA there?
        target.close()
    return steps, count, time.perf_counter() - started


if __name__ == "__main__":
    steps, count, seconds = drill(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    for name, ok in steps:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"restored {count} orders in {seconds:.2f} s")
    sys.exit(0 if all(ok for _, ok in steps) else 1)
```

Now the full exercise, with real data. First create some orders in the running service and take a backup **inside the container** (where the database file is), then copy it out of the volume:

```bash run
docker compose up -d --no-deps --scale api=1 api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
./traffic.sh
echo "orders in the live service: order 20 exists -> HTTP $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/orders/20)"
docker compose exec -T api python - /data/pagebound.db /data/backups 3 < backup.py | sed -E 's/api-[0-9]{8}T[0-9]{6}Z/api-STAMP/; s/pagebound-[0-9]{8}T[0-9]{6}Z/pagebound-STAMP/; s/sha256=[0-9a-f]+/sha256=.../'
rm -rf backups && docker compose cp api:/data/backups ./backups > /dev/null 2>&1
ls backups | sed -E 's/[0-9]{8}T[0-9]{6}Z/STAMP/'
```
```text
orders in the live service: order 20 exists -> HTTP 200
backup ok: pagebound-STAMP.db sha256=......
pagebound-STAMP.db
pagebound-STAMP.db.sha256
```

Next, **the drill**. We do it right now, while nothing is wrong, because that is the only time it is calm:

```bash run
BACKUP=$(ls backups/*.db | tail -1)
python restore_drill.py "$BACKUP" 20 | sed -E 's/ in [0-9.]+ s/ in N s/'
echo "--- and the drill catches a damaged backup:"
cp "$BACKUP" damaged.db && cp "$BACKUP.sha256" damaged.db.sha256
printf 'garbage' >> damaged.db                              # simulate a few corrupted bytes
python restore_drill.py damaged.db 20 | head -1
rm damaged.db damaged.db.sha256
```
```text
  PASS  checksum matches
  PASS  integrity check ok
  PASS  table 'orders' exists
  PASS  at least 20 order(s) present
restored 120 orders in N s
--- and the drill catches a damaged backup:
  FAIL  checksum matches
```

Now the disaster. Someone runs `docker compose down -v` (or the server disk fails). The volume with the database is gone:

```bash run
docker compose down -v > /dev/null 2>&1
echo "--- disaster: containers and the data volume are gone"
docker volume ls --filter name=^pbtut_api-data -q | wc -l | sed 's/^/data volumes left: /'
docker compose up -d --wait api nginx > /dev/null 2>&1
echo "service is back, but empty: order 1 -> HTTP $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/orders/1)"
```
```text
--- disaster: containers and the data volume are gone
data volumes left: 0
service is back, but empty: order 1 -> HTTP 404
```

The service is up and healthy, and has lost everything. This is the moment the backup is for. Restore by writing the backup file into the volume as the database, with the right owner (the service runs as user 10001), then restart the API:

```bash run
BACKUP=$(ls backups/*.db | tail -1)
docker compose stop api > /dev/null 2>&1
docker run --rm -v pbtut_api-data:/data -v "$PWD/backups:/backups:ro" python:3.14-slim \
    sh -c "cp /backups/$(basename "$BACKUP") /data/pagebound.db && chown 10001:10001 /data/pagebound.db && ls -l /data/pagebound.db | awk '{print \$3, \$5, \$9}'"
docker compose start api > /dev/null 2>&1
for i in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:18080/readyz)" = 200 ] && break; sleep 1; done
echo "after the restore: order 1 -> HTTP $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/orders/1), order 20 -> HTTP $(curl -s -o /dev/null -w '%{http_code}' localhost:18080/orders/20)"
curl -s localhost:18080/orders/20
```
```text
10001 8192 /data/pagebound.db
after the restore: order 1 -> HTTP 200, order 20 -> HTTP 200
{"id":20,"item":"item-20","quantity":1}
```

The data is back. Look at what the drill taught: copying files into a volume needed the right **ownership** (without `chown`, the application could not write to its database); the **data written after the last backup is lost** (that gap is your RPO); and the service is only fully back once readiness is green. These are exactly the details that go wrong at 3 a.m. if nobody practised. Write them in the runbook (section 14).

### 13.3 Tutorial: PostgreSQL backup and restore

Real systems usually use PostgreSQL. The tools are different, the discipline is the same. We run a throw-away Postgres in a container with its own volume, create data, back it up with `pg_dump`, destroy everything, and restore.

```bash run
docker run -d --name pbtut-pg -e POSTGRES_PASSWORD=drill-password -e POSTGRES_DB=shop -v pbtut-pgdata:/var/lib/postgresql/data postgres:16-alpine > /dev/null
for i in $(seq 1 60); do docker exec pbtut-pg pg_isready -U postgres -d shop -q 2>/dev/null && break; sleep 1; done
sleep 3
docker exec -i pbtut-pg psql -U postgres -d shop -q <<'SQLEOF'
CREATE TABLE orders (id serial PRIMARY KEY, item text NOT NULL, quantity int NOT NULL);
INSERT INTO orders (item, quantity) SELECT 'item-' || g, g FROM generate_series(1, 1000) g;
SQLEOF
echo "data before the backup:"
docker exec pbtut-pg psql -U postgres -d shop -t -A -c "SELECT count(*) || ' rows, quantity sum ' || sum(quantity) FROM orders"
```
```text
data before the backup:
1000 rows, quantity sum 500500
```

`pg_dump` makes a logical backup: the SQL needed to rebuild the database. The **custom format** (`-Fc`) is compressed and lets `pg_restore` restore selected tables or run in parallel:

```bash run
docker exec pbtut-pg pg_dump -U postgres -Fc shop -f /tmp/shop.dump
docker exec pbtut-pg ls -l /tmp/shop.dump | awk '{print "dump file: " $5 " bytes"}' | sed -E 's/[0-9]+ bytes/N bytes/'
docker cp pbtut-pg:/tmp/shop.dump ./shop.dump
echo "--- disaster: the container and its volume are destroyed"
docker rm -f pbtut-pg > /dev/null
docker volume rm pbtut-pgdata > /dev/null
echo "--- restore into a brand new database"
docker run -d --name pbtut-pg2 -e POSTGRES_PASSWORD=drill-password -e POSTGRES_DB=shop postgres:16-alpine > /dev/null
for i in $(seq 1 60); do docker exec pbtut-pg2 pg_isready -U postgres -d shop -q 2>/dev/null && break; sleep 1; done
sleep 3
echo "tables in the new database before the restore: $(docker exec pbtut-pg2 psql -U postgres -d shop -t -A -c "SELECT count(*) FROM pg_tables WHERE schemaname='public'")"
docker cp ./shop.dump pbtut-pg2:/tmp/shop.dump
docker exec pbtut-pg2 pg_restore -U postgres -d shop --no-owner /tmp/shop.dump && echo "pg_restore finished without errors"
echo "data after the restore:"
docker exec pbtut-pg2 psql -U postgres -d shop -t -A -c "SELECT count(*) || ' rows, quantity sum ' || sum(quantity) FROM orders"
docker rm -f pbtut-pg2 > /dev/null
rm -f shop.dump
```
```text
dump file: N bytes
--- disaster: the container and its volume are destroyed
--- restore into a brand new database
tables in the new database before the restore: 0
pg_restore finished without errors
data after the restore:
1000 rows, quantity sum 500500
```

The same 1,000 rows and the same checksum-like total (the sum of quantities) came back: **compare something other than "no errors"** after every restore. Notes for real PostgreSQL operations:

| Topic | What to know |
|---|---|
| **Logical backups** (`pg_dump`) | simple and portable; good for small and medium databases; restoring a big one takes a long time (so RTO grows with data) |
| **Physical backups + WAL archiving** (`pg_basebackup`, tools like pgBackRest or WAL-G) | copy the data files and ship the write-ahead log; allows **point-in-time recovery (PITR)**: restore to 10:41:00, just before the bad `DELETE`; RPO of seconds |
| **Managed databases** (RDS, Cloud SQL, Neon, Supabase, ...) | do automated snapshots and PITR for you; you still need to **test a restore** and to know the retention period |
| **Roles and globals** | `pg_dump` does not include roles; use `pg_dumpall --globals-only` |
| **Version differences** | restore with a `pg_restore` at least as new as the `pg_dump` that made the file |

### 13.4 Make it routine

- **Automate**: a nightly job (cron, a systemd timer, a scheduled container or your platform's scheduler) runs the backup script, copies the result **off the machine** (an object-storage bucket with `aws s3 cp`/`rclone`, a different provider, versioned and write-protected), and **encrypts** it (for example with `age` or `gpg`) so that a stolen backup is useless.
- **Monitor the backups themselves.** The classic failure is a backup job that quietly stopped months ago. Have the job ping a "dead-man's switch" service (such as Healthchecks.io) on success; if the ping does not arrive on time, you get an alert. Export "age of the newest backup" as a metric and alert when it exceeds your RPO.
- **Run the restore drill on a schedule** (at least quarterly) in a clean environment, time it, and write down the result. The drill report has: date, which backup, **how long the restore took** (your measured RTO), **how old the data was** (your measured RPO), what went wrong, and what you changed.
- **Practise the human part:** who decides to restore, who does it, who tells the users. A drill with real people finds gaps no script can.
- **Protect against deletion:** the account that writes backups should not be able to delete them (immutable or versioned storage) so ransomware or a mistake cannot remove the safety net.

```bash run
cat <<'EOF'
# crontab -e   (every night at 02:30, UTC server time; the dead-man's-switch ping only happens if the backup worked)
30 2 * * *  cd /srv/pagebound && docker compose exec -T api python - /data/pagebound.db /data/backups 14 < backup.py \
            && curl -fsS -m 10 https://hc-ping.com/YOUR-UUID > /dev/null
EOF
```
```text
# crontab -e   (every night at 02:30, UTC server time; the dead-man's-switch ping only happens if the backup worked)
30 2 * * *  cd /srv/pagebound && docker compose exec -T api python - /data/pagebound.db /data/backups 14 < backup.py \
            && curl -fsS -m 10 https://hc-ping.com/YOUR-UUID > /dev/null
```

### Try it: RPO and RTO

A shop takes a backup every night at 02:00. At 15:30 an operator drops the wrong table. Restoring takes 45 minutes. What are the RPO and RTO of this setup, and what is the cheapest improvement?

<details><summary>Answer</summary>

The **RPO** is up to 24 hours (everything since 02:00 is lost: here 13.5 hours of orders), and the **RTO** is about 45 minutes plus the time to notice and to decide. Cheapest improvement: more frequent backups (every hour, or continuous log shipping with point-in-time recovery for PostgreSQL), which shrinks the RPO; and a rehearsed runbook, which shrinks the RTO. Whether it is worth it depends on what an hour of lost orders costs the business: that number, not the technology, decides.

</details>

### Try it: what did the drill not test?

Our SQLite drill restored the file and counted the orders. Name two things it could miss that a real recovery needs.

<details><summary>Answer</summary>

(1) That the **application** works with the restored database (the right version, migrations, file ownership and permissions: we hit the ownership problem in the disaster exercise). (2) Everything outside the database: **uploaded files, secrets, configuration**, the Redis state (here disposable) and DNS or certificates for a replacement server. A full drill rebuilds the whole service on clean infrastructure from backups and the repository and checks a real user flow.

</details>

## 14. Operating it: runbooks, incidents and routine care

### 14.1 Runbooks

An alert at 3 a.m. should not require genius, only a checklist. A **runbook** is a short page per alert or per task: *what it means, how bad it is, how to check, how to fix, who to call.* Write it when you create the alert. Here is one for the alert of section 10.5, using only commands from this chapter:

```text
RUNBOOK: HighErrorRate  (more than 5% of requests fail)

Impact     Users see errors. Page severity.
First 2 minutes
  1. Was there a deployment in the last 30 minutes?  (CI run / ./deploy.sh output / `git log -3`)
       yes -> roll back first:  ./deploy.sh <previous version>   then investigate.
  2. Dashboards: which route and which status?      (Prometheus: sum by (route, status) (rate(http_requests_total[1m])))
Diagnose
  3. Take one failing request id from a user report or from the logs:
       docker compose logs api --no-log-prefix | grep '^{' | jq -c 'select(.level=="ERROR") | {request_id, msg}' | tail
  4. Follow the id through nginx and the app (section 8.4); read the traceback.
  5. Dependencies: curl localhost:18080/readyz   (which problem does it list: database? redis?)
Mitigate
  6. A dependency is down -> start it (`docker compose start redis`); the service recovers by itself.
  7. One endpoint is the cause -> disable it with its feature flag, or return 503 for it at nginx.
Escalate  if not mitigated in 15 minutes -> call <name>, <phone>.
After     write the postmortem (section 14.2); add what you learned to this page.
```

### 14.2 Incidents and postmortems

When something breaks in production, the work follows a pattern: **detect** (an alert or a user), **assess** (how many users, how bad? give it a severity), **mitigate** (stop the pain first: roll back, switch off a feature, add capacity, fail over), **communicate** (status page or message to users and the team, at regular intervals even if there is no news), **resolve**, and **learn**. Rules that make incidents shorter:

- **Mitigate before you diagnose.** Rolling back a release takes a minute; finding the root cause may take hours.
- **One person leads** (decides and keeps a timeline); others help with specific tasks. Write what you do and when, as you do it.
- **Change one thing at a time**, and note it.
- **Do not panic-deploy** untested fixes unless the alternative is worse.

Afterwards write a **blameless postmortem**: a short document about the *system* and not the person. People make mistakes; a system where one mistake takes it down needs better safeguards, not a better-behaved person. The usual sections:

```text
Summary      one paragraph: what broke, for how long, who was affected.
Timeline     UTC times: first sign, detection, each action, resolution.
Cause        the chain of events (and why our checks did not stop it).
What went well / what went badly / where we got lucky.
Actions      concrete items with an owner and a date: a test, an alert, a runbook step, a limit.
```

The value is in the **actions** and in actually doing them. Most mature teams track the same few causes: a deployment without a rollback plan, a missing alert, a dependency without a timeout, a backup that was never restored.

### 14.3 Routine care

Some work has no alert and no deadline and still causes outages when ignored. Put it in a calendar:

| What | How often | Why |
|---|---|---|
| Apply OS and Docker updates; rebuild images on a fresh base | monthly, and at once for critical fixes | security fixes |
| Update dependencies (Dependabot pull requests), run `pip-audit` | weekly | known vulnerabilities |
| Check certificate expiry | continuously by alert (30 days before) | an expired certificate is a full outage |
| Check free disk space, log and image growth | alert at 80% | full disks stop databases and logs |
| Rotate secrets and review access | quarterly, and when people leave | leaked or forgotten keys |
| Restore drill | quarterly | section 13 |
| Review alerts that fired: too noisy? missed something? | monthly | alert quality |
| Capacity and cost review | quarterly | surprises on the invoice or at peak |

Look at what our own containers are using right now; the numbers are the kind you would watch over time (memory and CPU are specific to this machine and moment, so yours will differ):

```bash run
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}' $(docker ps -q --filter name=^pbtut) | sort
```
```text
NAME                 MEM USAGE / LIMIT     CPU %
pbtut-api-1          45.71MiB / 6.981GiB   0.77%
pbtut-nginx-1        8.289MiB / 6.981GiB   0.00%
pbtut-prometheus-1   31.19MiB / 6.981GiB   0.57%
pbtut-redis-1        3.547MiB / 6.981GiB   1.72%
```

### 14.4 A server's basic security

- **SSH with keys only** (disable password logins: `PasswordAuthentication no`), no direct root login, and a non-default user.
- **A firewall that denies by default** and allows only 22, 80 and 443 (`ufw`); internal services (databases, Redis, Prometheus) listen on `127.0.0.1` or a private network and are **never** published to the internet. We did this throughout the chapter with `127.0.0.1:` in every `ports:` entry.
- **Automatic security updates** (`unattended-upgrades` on Debian and Ubuntu) and a reboot plan.
- **fail2ban** or similar to slow down brute-force logins.
- **Least privilege** for containers (non-root user, read-only filesystem where possible, no `--privileged`) and for people (separate accounts, no shared passwords).
- **Backups and monitoring on from day one**, not after the first disaster.

### 14.5 A habit of mind

Prefer **boring technology** you understand over fashionable technology you do not; add a tool only when a concrete problem justifies it (you do not need Kubernetes for one small service on one server). Prefer **small, reversible changes**. Prefer **automation of what you do twice**, and **documentation of what you do rarely**. Measure first, then optimise. And when you build any feature, ask the operations question: *how will I know it is broken, and how will I turn it off?*

### Try it: write the runbook

Write a five-line runbook for the alert "disk usage above 85%" on the server that runs this Compose stack. Which commands would you list first?

<details><summary>Answer</summary>

(1) `df -h` to confirm and find the full filesystem. (2) `docker system df` to see whether images, containers or volumes are the cause (and `du -sh /var/lib/docker/containers/*/*-json.log` for runaway container logs: set `max-size` in the logging options, section 8.6). (3) Remove only what you know is safe: old unused images of **your** project (`docker image rm pagebound-api:<old version>`), rotated logs, old backups beyond retention. (4) Check what grew (a bug writing logs, a missing cleanup). (5) Fix the cause, add the missing limit, and raise the alert threshold or capacity if growth is real. Do **not** start with `docker system prune -a` on a machine shared with other projects.

</details>

### Try it: first five minutes

An alert says the error rate is 40% and the last deployment was 12 minutes ago. What do you do in the first two minutes, and why in that order?

<details><summary>Answer</summary>

Roll back the deployment (`./deploy.sh <previous>`), because a recent change is the most likely cause, rollback is fast and safe by design (section 12), and it stops the pain for users. Only then look at dashboards and follow request ids to find the cause, with the pressure off. If the error rate stays at 40% after the rollback, the deployment was not the cause, and you have lost two minutes, not twenty. "Mitigate first, diagnose second."

</details>

## 15. Project: Dockerise, deploy and monitor your API with CI

### 15.1 The task

Take the API you built in swe.04 (Flask), swe.05 (FastAPI) or swe.06 (Django), or the Pagebound service of this chapter if you have none, and make it **operable**. The result is a repository where a stranger can run one command and get a working, monitored system, and where every change is tested and built automatically.

### 15.2 What the finished repository contains

Here is the file list of the Pagebound repository as built in this chapter (generated by the command shown; temporary files are filtered out):

```bash run
find . -type f -not -path './.git/*' -not -path './work/*' -not -name '*.pyc' -not -path '*/__pycache__/*' -not -name '*.log' -not -path './.mypy_cache/*' -not -name 'request_id.txt' \
    -not -path './backups/*' -not -path './site/*' -not -path './certs/*' -not -name 'demo.env' -not -name 'buildsteps.py' -not -name 'bad.yml' -not -name 'broken.yml' \
    -not -name 'codes.txt' -not -name '.current-version' -not -name 'gunicorn.pid' | sort | sed 's|^\./||'
```
```text
app/config.py
app/logs.py
app/main.py
app/metrics.py
asgi_demo.py
backup.py
check_workflow.py
compose.yaml
deploy.sh
Dockerfile
.dockerignore
.env
.env.example
.github/dependabot.yml
.github/workflows/ci.yml
.gitignore
gunicorn.conf.py
Makefile
monitoring/alerts.yml
monitoring/prometheus.yml
nginx/default.conf
requirements.txt
restore_drill.py
tests/test_app.py
traffic.sh
wsgi_demo.py
```

### 15.3 The steps

1. **Configuration** (section 3): a `Settings` object that reads the environment, validates, fails fast, hides secrets. A `.env.example`, a real `.env` ignored by git.
2. **Server** (section 2): a production server command with sensible worker settings (`uvicorn` for FastAPI; `gunicorn` for Flask or Django with `workers`, `timeout`, `graceful_timeout`).
3. **Logging** (section 8): JSON logs to stdout with a request id on every line; error responses that carry the id and nothing else.
4. **Health** (section 9): `/healthz` (liveness, no dependencies) and `/readyz` (dependencies, drain flag).
5. **Metrics** (section 10): a `/metrics` endpoint with request counts and latency histograms by route template.
6. **Docker** (section 5): a Dockerfile with a slim pinned base, dependencies before code, non-root user, `HEALTHCHECK`, exec-form `CMD`, a `.dockerignore`.
7. **Compose** (section 6): the app, its backing services (Redis, PostgreSQL if you use it), volumes, health-based `depends_on`, restart policies, ports bound to `127.0.0.1`, log rotation.
8. **Proxy** (section 7): Nginx with JSON access logs, request ids, forwarded headers, timeouts, a rate limit, TLS (self-signed locally).
9. **Monitoring** (section 10): Prometheus scraping the app, alert rules for down instances and high error rate, rules checked with `promtool`.
10. **CI** (section 11): a workflow that type-checks, tests (matrix), lints itself, builds the image, and pushes it on `main`; a `Makefile` so the same commands run locally.
11. **Deployment** (section 12): `deploy.sh` with health-gated rollout, version verification and automatic rollback; versioned image tags.
12. **Backups** (section 13): a backup script, off-machine copy, and a restore drill you have run and timed.
13. **Runbook** (section 14): a page for each alert and for "deploy", "roll back", "restore".

For **Flask or Django** the Dockerfile `CMD` becomes Gunicorn in exec form, for example `CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi_demo:app"]` (with `bind = "0.0.0.0:8000"` inside the container), and Django additionally needs `collectstatic` at build time, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` from the environment, and migrations run as a one-off command (`docker compose run --rm web python manage.py migrate`) before the new version starts (swe.06 section 17).

### 15.4 Game day: break it on purpose

A system is not operable until you have watched it fail. Run each drill and write down what you observed and what you would change. All use only commands from this chapter:

| Drill | How | What you should observe |
|---|---|---|
| **Kill the API** | `docker compose kill api` (all replicas) | nginx answers 504/502; the restart policy does *not* restart a container that was killed by hand; `docker compose start api` brings it back; the alert `InstanceDown` fires |
| **Stop a dependency** | `docker compose stop redis` | readiness red, liveness green, `/hits` fails with a request id; recovery without a restart (section 9.3) |
| **Bad configuration** | deploy a version that needs a missing variable | `deploy.sh` rolls back automatically (section 12.3) |
| **Traffic spike** | `for i in $(seq 1 500); do curl -s -o /dev/null localhost:18080/; done` | nginx returns `503` once the limit is exceeded; the error-rate panel and metric move |
| **A slow endpoint** | `curl localhost:18080/slow?seconds=8` | nginx times out after 5 s (and retries on other replicas: section 7.4); latency percentiles rise |
| **Lose the data** | `docker compose down -v`, then restore from a backup | the disaster and restore exercise of section 13.2, timed |
| **Full disk (simulated)** | set `max-size` very small on a service and send traffic | log files rotate instead of growing (section 8.6) |
| **Expired certificate** | create a certificate with `-days 0`... or 1 day, wait | browsers and `curl` refuse; a certificate-expiry alert would have warned you |

### 15.5 Acceptance checklist

- [ ] `git clone` plus `cp .env.example .env` plus `docker compose up -d --wait` gives a working system on a clean machine.
- [ ] `make ci` passes locally, and the same workflow is green on GitHub.
- [ ] An error response contains a request id, and following that id through the logs reaches the traceback (section 8.4).
- [ ] Killing a container, stopping Redis, and deploying a broken release each recover as designed (game day).
- [ ] A deployment with a bad configuration rolls back by itself; a manual rollback to an older version works without rebuilding.
- [ ] Prometheus shows all instances up; the high-error-rate alert fires when you cause errors.
- [ ] A backup exists off the machine, and you have restored it into a clean environment and written down how long it took.
- [ ] No secret is in git, in the image, in logs or on a command line; `.env` is ignored.
- [ ] Every internal service is bound to `127.0.0.1` or a private network.
- [ ] Runbooks exist for the alerts, the deployment, the rollback and the restore.

## 16. Common traps

1. **`flask run` / `uvicorn --reload` in production**; one sync worker for a slow endpoint (2).
2. **Secrets in the image, in `ENV`, on a command line or in git** (3.5, 5.6).
3. **`latest` tags and unpinned dependencies**: you cannot say what is running, and cannot roll back (5.6, 12.1).
4. **`COPY . .` before `pip install`**: every code change reinstalls everything (5.3).
5. **Shell-form `CMD` or plain Python as PID 1**: `SIGTERM` is ignored, every stop takes 10 seconds and kills requests (4.3, 5.5).
6. **Running as root** in the container (5.2).
7. **Publishing ports on all interfaces** (`-p 8000:8000`), and trusting `ufw` to protect Docker ports (4.3, 12.6).
8. **Data in the container filesystem instead of a volume**; `down -v` as a reflex (4.4, 6.3).
9. **`localhost` inside a container** meaning the container itself (4.5).
10. **Plain `depends_on`** (start order only) instead of a health condition (6.2).
11. **Nginx resolving the upstream name once** (stale addresses after a redeploy or a scale-up) and retrying timeouts on every replica (7.3, 7.4).
12. **Reloading Nginx without `nginx -t`**, or editing a file that is not the mounted one (7.7).
13. **Untrusted `X-Forwarded-For`** or the proxy's address seen as every client (2.5, 7.2).
14. **Unstructured logs with no request id**, secrets in logs, a log line for every health probe, no log rotation (8, 8.6).
15. **A liveness check that tests dependencies** (restart storms), and no readiness or drain (9.1, 9.5).
16. **High-cardinality metric labels** (raw paths, user ids), averages instead of percentiles, counters read without `rate` (10.2, 10.4).
17. **Alerts on causes instead of symptoms**, with no runbook, or so many that nobody reads them (10.6).
18. **Logic in the CI YAML** that you cannot run locally; unpinned third-party actions; secrets in `run:`; `pull_request_target` (11).
19. **Deploying by hand-editing a server**, with no recorded previous version and no health-gated rollout (12).
20. **Rebuilding the old code to "roll back"**, or destructive migrations in the same release as the code change (12.1, 12.4).
21. **Backups that were never restored**, only on the same machine, never monitored, and never encrypted (13).
22. **Copying a live SQLite file** instead of using the backup API (13.2).
23. **`docker system prune` on a shared machine** (4.7, 14.5).
24. **Treating the first incident as the moment to learn the tools** instead of practising game days (15.4).

## 17. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| `docker stop` takes 10 seconds | the process ignores `SIGTERM` (PID 1, shell-form CMD) | 4.3, 5.5 |
| exit code 137 | out-of-memory kill, or `SIGKILL` after the grace period | 4.6 |
| the rebuild reinstalls all dependencies | code copied before `requirements.txt` | 5.3 |
| connection refused to the database from a container | `localhost` means the container; use the service name | 4.5 |
| the app starts before its database is ready | `depends_on` without `service_healthy` | 6.2 |
| `variable is not set` from Compose | missing `.env` entry (the `:?` check worked) | 6.2 |
| nginx 502 right after a redeploy | stale upstream address; the app is down or restarting | 7.3, 7.4 |
| nginx 504 on slow requests, repeated calls | `proxy_read_timeout`, retries on other replicas | 7.4 |
| scaled up and no new traffic arrives | nginx resolved the name once | 7.3 |
| every request comes from the same IP in the app | missing forwarded headers or `--proxy-headers` | 2.5, 7.2 |
| `jq: parse error` on container logs | non-JSON lines (server messages) mixed in; filter with `grep '^{'` | 8.3 |
| container `unhealthy` but not restarted | Docker/Compose only report; orchestrators act | 9.3 |
| all instances restart when the database is down | liveness depends on the database | 9.1 |
| Prometheus shows no data for a metric | target down or wrong port; `rate` needs two scrapes in the range | 10.3 |
| memory growth in Prometheus | high-cardinality labels | 10.2 |
| CI green locally, red on GitHub (or the reverse) | unpinned versions, ignored files, environment differences | 11.7 |
| `on` key missing when parsing a workflow in Python | YAML 1.1 reads `on` as `True` | 11.5 |
| rollback "worked" but behaves like the new code | the old version was rebuilt, not reused | 12.1 |
| old code errors after a deploy | a destructive schema change in the same release | 12.4 |
| restored database cannot be written | file ownership in the volume | 13.2 |
| backup job silently stopped | no dead-man's switch, no age metric | 13.4 |
| disk full | unrotated container logs, old images, old backups | 8.6, 14.5 |

## 18. Summary

- **Operations** closes the gap between "works on my laptop" and "runs reliably for users": start, configure, watch, ship, undo, recover. Build once, deploy many; configuration comes from the environment.
- **Gunicorn** (WSGI, pre-fork master and workers) and **Uvicorn** (ASGI) run Python apps for real. Worker count is your concurrency; a worker that exceeds the timeout is killed; `SIGHUP` reloads gracefully and `SIGTERM` stops gracefully.
- **Configuration** is read once into a validated object that fails fast and hides secrets. Secrets never go into images, git, logs or command lines.
- **Docker** packages an app as an immutable image; containers are isolated processes. Order the Dockerfile for the cache (dependencies before code), run as non-root, use the exec form for `CMD` so `SIGTERM` arrives, add a `HEALTHCHECK`, pin versions, never deploy `latest`. Data lives in volumes; containers on a user-defined network reach each other by name.
- **Compose** describes the whole system in one file: services, volumes, health-gated `depends_on`, restart policies, local-only ports, log rotation.
- **Nginx** is the front door: TLS, forwarded headers, timeouts, rate limits, request ids, load balancing. Beware resolve-once upstreams and retries of timed-out requests; always `nginx -t` before `nginx -s reload`.
- **Structured JSON logs with a request id** make one failing request traceable from the proxy to the traceback with `jq`. Rotate container logs. Do not log secrets or health probes.
- **Health checks:** liveness answers only "is this process broken?"; readiness covers dependencies and draining; graceful shutdown finishes in-flight requests.
- **Metrics:** counters, gauges, histograms; RED for services; percentiles not averages; bounded label cardinality. **Prometheus** scrapes and answers PromQL; alert on symptoms, with runbooks. SLOs and error budgets turn reliability into a number.
- **CI (GitHub Actions)** builds and tests every change on a clean machine; keep the logic in a Makefile; least-privilege tokens, pinned actions, secrets through `env:`.
- **Deploying:** versioned immutable images, health-gated rollout, post-deploy verification, automatic rollback, and rollback by reusing the old image; compatible (expand and contract) database changes; roll back first, investigate second.
- **Backups** are copies with a purpose (RPO, RTO), kept off-site and encrypted, taken with the database's own tools, **monitored**, and **restored in drills**. A backup that was never restored is a hope.
- **Operate calmly:** runbooks, blameless postmortems, routine maintenance, a firewalled server with internal services on private interfaces, and game days that break things on purpose.

Next: the 30 problems for this module practise reading Dockerfiles, Compose files and Nginx configs, finding bugs in them, tracing requests through logs, writing health checks and metrics, reading CI workflows, planning rollbacks and backup drills, and building small operational scripts.
