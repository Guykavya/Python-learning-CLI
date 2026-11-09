# Chapter 8 (SWE): Caching, queues and background work

Until now, every request in this course did all its work **before** answering, and every answer was computed **from scratch**. That is fine for a small app and a few users. As soon as traffic grows, two problems appear:

1. **Reads are repeated.** A thousand visitors ask for the same product page, and the database answers the same question a thousand times. A **cache** keeps the answer close and cheap.
2. **Some work is slow or unreliable.** Sending an e-mail, building a PDF report, resizing an image or calling a payment provider should not make a user stare at a spinner, and it should not be lost if the server restarts. A **queue** lets the web request say "please do this" and answer at once, while a **worker** does the job in the background.

Both tools make a system faster and more reliable, and both create **new ways to be wrong**: a cache can show stale or even someone else's data; a queue can lose a job, run it twice, or run a broken job forever. This chapter teaches the tools together with their failure modes. You will build working versions of the important pieces yourself, so nothing is magic.

By the end you reach two outcomes:

- You can **design a worker that gives the same result when a task runs twice**, and prove it with tests that crash the worker at every awkward moment (section 11).
- You can **build an e-mail and report worker that survives crashes**: you will kill the worker process in the middle of a job and show that, after a restart, the report exists exactly once and the e-mail was sent exactly once (section 16).

Prerequisites: swe.03 (SQL and transactions), swe.05 (FastAPI; background tasks in section 14), swe.07 (idempotency keys, rate limiting, locks of a kind). Concurrency basics (threads, processes) come from core.21.

> **Offline rule for this chapter.** Redis, Celery, RQ and arq are not installed in this course environment, and the course must work without a network. So the exercises run on two things you can read completely: **`MiniRedis`**, a small in-process stand-in for the Redis commands we need (same method names and return values as the `redis` Python package), and a **durable job queue built on SQLite** that has leases, retries and a dead-letter state. The ideas are identical to the real systems; the real tools appear in clearly marked **Try it on your machine** steps with exact commands and no invented output. Every other output in this chapter was produced by running the code above it, with these versions (patch versions may differ):

```bash run
python -c "
import sys, sqlite3, fastapi, pydantic
print('python  ', sys.version.split()[0])
print('sqlite  ', sqlite3.sqlite_version)
print('fastapi ', fastapi.__version__)
print('pydantic', pydantic.__version__)
"
```
```text
python   3.14.4
sqlite   3.46.1
fastapi  0.162.0
pydantic 2.14.3
```

## Table of contents

1. [Why caches and queues, and what can go wrong](#1-why-caches-and-queues-and-what-can-go-wrong)
2. [Caching fundamentals](#2-caching-fundamentals)
3. [Redis in a nutshell](#3-redis-in-a-nutshell)
4. [Cache-aside in practice](#4-cache-aside-in-practice)
5. [Cache invalidation](#5-cache-invalidation)
6. [Cache stampedes, avalanches and hot keys](#6-cache-stampedes-avalanches-and-hot-keys)
7. [Other jobs for Redis: sessions, counters, locks, events](#7-other-jobs-for-redis-sessions-counters-locks-events)
8. [Queues and background work: the ideas](#8-queues-and-background-work-the-ideas)
9. [Building a durable job queue](#9-building-a-durable-job-queue)
10. [Workers](#10-workers)
11. [Idempotent workers: the same result when a task runs twice](#11-idempotent-workers-the-same-result-when-a-task-runs-twice)
12. [Retries, backoff and dead letters](#12-retries-backoff-and-dead-letters)
13. [Task-queue libraries: Celery, RQ and arq](#13-task-queue-libraries-celery-rq-and-arq)
14. [Scheduled jobs](#14-scheduled-jobs)
15. [Operating caches and queues](#15-operating-caches-and-queues)
16. [Project: an e-mail and report worker that survives crashes](#16-project-an-e-mail-and-report-worker-that-survives-crashes)
17. [Common traps](#17-common-traps)
18. [Collected traps](#18-collected-traps)
19. [Summary](#19-summary)

## 1. Why caches and queues, and what can go wrong

### 1.1 Three problems, two tools

| Problem | Example | Tool |
|---|---|---|
| The same read is expensive and repeated | the home page runs 12 queries for every visitor | **cache** |
| The work is slow | a monthly report takes 40 seconds | **queue + worker** |
| The work must not be lost, but the caller cannot wait | "send the welcome e-mail" after sign-up | **queue + worker** |
| A traffic spike would crush a dependency | 5,000 sign-ups in a minute call the e-mail provider | **queue** (absorbs the spike) |
| Something must happen at certain times | invoices every month, clean-up every night | **scheduled jobs** (section 14) |

```text
                  cache hit
   browser ---> web app ----------> cache (Redis)         read path: fast, may be stale
                  |   \ miss
                  |    `--------->  database
                  |
                  | enqueue "send e-mail"                 write path: answer now,
                  v                                        do the slow part later
              queue / broker  --->  worker  --->  e-mail provider, report files, ...
```

### 1.2 Typical costs

The numbers below are rough orders of magnitude on ordinary hardware (they vary by machine and network), but the ratios are what matter:

| Operation | Rough time |
|---|---|
| read a Python dict or object attribute | 0.00005 ms (50 ns) |
| read from Redis on the same network | 0.2 to 1 ms |
| simple indexed database query | 1 to 10 ms |
| complex query or join | 10 ms to seconds |
| call an external HTTP API | 50 to 1,000 ms |
| send an e-mail through a provider | 200 ms to several seconds |

A cache hit that replaces a 20 ms query with a 0.5 ms lookup is 40 times faster, and it also removes load from the database, which is usually the hardest part of the system to scale.

### 1.3 What can go wrong (the map of this chapter)

| Tool | Failure | Plain words | Section |
|---|---|---|---|
| Cache | **stale data** | the cache shows the old price after an update | 5 |
| Cache | **stampede** | a popular key expires and 500 requests hit the database at once | 6 |
| Cache | **leaking data** | a per-user answer stored under a shared key | 4 |
| Cache | **cold start / eviction** | the system is only fast while the cache is warm | 2 |
| Queue | **lost job** | the server restarted and the job vanished | 8, 9 |
| Queue | **duplicate job** | the job ran twice (two e-mails, two charges) | 11 |
| Queue | **poison job** | a bad job fails and retries for ever | 12 |
| Queue | **silent backlog** | the queue grows and nobody notices | 15 |
| Schedules | **double or missed runs** | two schedulers run the nightly job twice; a restart skips it | 14 |

The common theme: **a cache is a copy and a queue is a promise.** A copy can be out of date; a promise can be broken or kept twice. Good design says clearly what happens in each case.

### Try it: cache or queue?

Choose a cache, a queue, or neither for each: (a) a news site's front page, rebuilt from 20 queries, viewed 50 times a second; (b) turning an uploaded video into three resolutions; (c) checking whether a username is taken during sign-up; (d) charging a card when the user presses "Pay".

<details><summary>Answer</summary>

(a) **Cache**: the same expensive read, a few seconds of staleness is fine. (b) **Queue**: slow, can happen after the upload completes; show "processing". (c) **Neither, or a very short cache**: it must be correct (a stale "free" answer causes a duplicate-name error); the database with a unique index is the truth, and a fast indexed query is cheap. (d) **Neither as a plain background job**: the user needs the outcome now. Do the charge in the request (with an idempotency key, swe.07 section 13), and queue the *follow-up* work (receipt e-mail, invoice PDF).

</details>

## 2. Caching fundamentals

### 2.1 Hits, misses and the hit ratio

A **cache** stores the result of an expensive operation under a **key**. A lookup is a **hit** if the key is present and a **miss** if not. The **hit ratio** is `hits / (hits + misses)`. A cache with a 95% hit ratio sends only 1 request in 20 to the database. A cache with a 20% hit ratio costs you extra complexity for almost nothing, so measure it.

Caching works because real traffic is **skewed**: a few items (the best-selling product, today's headlines) get most of the requests. It does not help for data that is read once.

### 2.2 Where to cache

You can cache at several layers, nearest to the user first:

| Layer | Example | Shared by | Notes |
|---|---|---|---|
| Browser | `Cache-Control: max-age=3600` | one user | free, but you cannot clear it remotely |
| CDN / reverse proxy | Cloudflare, Nginx, Varnish | all users | great for public pages and images |
| **Application memory** | a dict or `lru_cache` in each process | one process | fastest; every worker has its own copy |
| **Shared cache** | Redis, Memcached | all workers | the common choice for "the" cache |
| Database | query cache, materialised views | all | do not forget that indexes are a cache too |

### 2.3 What is cacheable

Good candidates: results that are **expensive**, **read often**, **change rarely**, and where **a little staleness is acceptable** (product descriptions, configuration, leaderboards, rendered fragments, results of external API calls). Poor candidates: data that must be exact at every moment (account balances, stock when selling the last item, permissions), and data that is different for each user unless the key says so (section 4.4).

### 2.4 Time to live and eviction

Every cached value should have a **time to live (TTL)**: after that many seconds it counts as missing. A TTL is your safety net: even if an invalidation bug leaves old data behind, it disappears eventually. A cache also has **limited memory**, so when it is full it must **evict** something. Common policies:

| Policy | Evicts | Good for |
|---|---|---|
| **LRU** (least recently used) | the item not touched for the longest time | general use |
| **LFU** (least frequently used) | the item used least often | stable popularity |
| **TTL** only | whatever expires | simple |
| **FIFO** | the oldest inserted | rarely best |

### 2.5 An in-process TTL + LRU cache

Python's `functools.lru_cache` (swe.05 section 18) is an in-process LRU cache with no expiry. A small class adds the time to live. The clock is a parameter, so tests move time instead of sleeping:

```python
# ttlcache.py
import time
from collections import OrderedDict


class TTLCache:
    """Bounded cache: entries expire after `ttl` seconds; the least recently used entry is dropped when full."""

    def __init__(self, maxsize=128, ttl=60.0, now=time.monotonic):
        self.maxsize, self.ttl, self.now = maxsize, ttl, now
        self._items: OrderedDict = OrderedDict()           # key -> (expires_at, value)
        self.hits = self.misses = 0

    def get(self, key, default=None):
        entry = self._items.get(key)
        if entry is None or entry[0] <= self.now():
            if entry is not None:
                del self._items[key]                       # expired: remove it lazily
            self.misses += 1
            return default
        self._items.move_to_end(key)                       # mark as most recently used
        self.hits += 1
        return entry[1]

    def set(self, key, value, ttl=None):
        self._items[key] = (self.now() + (self.ttl if ttl is None else ttl), value)
        self._items.move_to_end(key)
        while len(self._items) > self.maxsize:
            self._items.popitem(last=False)                # evict the least recently used

    def delete(self, key):
        self._items.pop(key, None)

    def __len__(self):
        return len(self._items)

    @property
    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
```

```python run
from ttlcache import TTLCache

clock = [0.0]
cache = TTLCache(maxsize=3, ttl=10, now=lambda: clock[0])

for key in "abc":
    cache.set(key, key.upper())
print("a:", cache.get("a"), "| size", len(cache))
cache.set("d", "D")                                   # full: evicts the least recently used (b, since a was just read)
print("after adding d -> b:", cache.get("b"), "| a:", cache.get("a"), "| d:", cache.get("d"))

clock[0] = 10.0                                       # exactly the ttl: expired
print("after 10 s -> a:", cache.get("a"))

import random
random.seed(7)
cache2 = TTLCache(maxsize=10, ttl=1000, now=lambda: clock[0])
keys = [min(int(random.paretovariate(1.2)), 30) for _ in range(2000)]      # skewed traffic: a few keys dominate
for k in keys:
    if cache2.get(k) is None:
        cache2.set(k, f"value-{k}")
print(f"2000 skewed requests, room for 10 items: hit ratio {cache2.hit_ratio:.0%}")
```
```text
a: A | size 3
after adding d -> b: None | a: A | d: D
after 10 s -> a: None
2000 skewed requests, room for 10 items: hit ratio 91%
```

The last line shows why caches work: with room for only 10 of ~30 possible keys, most requests are still hits, because a few keys are very popular. An in-process cache like this one is fast, but **every worker process has its own copy**, so a change in one worker is not seen by the others, and the total memory is multiplied. That is why most systems use a **shared** cache such as Redis.

### Try it: size the cache

A cache holds 100 items. Requests cycle through 101 different keys in order (1, 2, ..., 101, 1, 2, ...). What hit ratio do you get with LRU, and what does this teach?

<details><summary>Answer</summary>

Zero (after the first pass). When you ask for key 101, key 1 was the least recently used and has just been evicted; then you ask for key 1 (miss, which evicts 2), then key 2 (miss), and so on: every request misses. Sequential scans over data slightly larger than the cache defeat LRU. The lesson: measure the hit ratio with realistic traffic, and know that one big scan (a report that touches every row) can flush a cache of useful hot items.

</details>

## 3. Redis in a nutshell

### 3.1 What Redis is

**Redis** is an in-memory data store accessed over the network, usually by one or more application servers. It is not "just a cache": it has **data structures**, **expiry**, **atomic operations** and (optionally) persistence. Its commands run one at a time on a single thread, so each command is **atomic**: nothing can interleave inside a single `INCR`. That property makes it the standard tool for shared counters, rate limits, locks, sessions, queues and caches.

| Structure | Commands (examples) | Typical use |
|---|---|---|
| **String** | `SET`, `GET`, `INCR`, `EXPIRE`, `TTL` | cache values, counters, locks, flags |
| **Hash** | `HSET`, `HGET`, `HGETALL`, `HINCRBY` | an object with fields (a session, a profile) |
| **List** | `LPUSH`, `RPOP`, `BRPOP`, `LRANGE` | simple queues, recent items |
| **Set** | `SADD`, `SMEMBERS`, `SISMEMBER` | tags, unique visitors |
| **Sorted set** | `ZADD`, `ZRANGE`, `ZINCRBY` | leaderboards, delayed jobs (score = time) |

Honest limits: Redis keeps data in **memory**, so capacity is RAM; persistence (RDB snapshots, an append-only file) reduces but does not remove the chance of losing the last seconds of writes; and a cache that evicts keys when memory is full (`maxmemory-policy allkeys-lru`) will happily throw away your data. **Use Redis for data you can recreate, or configure and treat it as a database deliberately.**

### 3.2 MiniRedis: the same commands, in 100 lines

To practise without installing a server, here is `MiniRedis`. It follows the conventions of the `redis` Python package created with `decode_responses=True` (strings in, strings out): `set(..., nx=True)` returns `True` or `None`, `ttl` returns `-2` for a missing key and `-1` for no expiry, `lrange` includes its end index, and so on. It takes a clock so tests control time, and a lock so that each command is atomic. Real Redis does much more (Lua scripts, pub/sub, streams, transactions), which we only describe.

```python
# miniredis.py
import fnmatch
import math
import threading
import time


class MiniRedis:
    """A small in-process stand-in for the Redis commands used in this chapter."""

    def __init__(self, now=time.time):
        self.now = now
        self._data, self._expires = {}, {}
        self._lock = threading.RLock()                       # one command at a time, like Redis

    # ---- internals
    def _alive(self, key):
        deadline = self._expires.get(key)
        if deadline is not None and deadline <= self.now():
            self._data.pop(key, None)
            self._expires.pop(key, None)
        return key in self._data

    def _get_typed(self, key, kind, create=None):
        if not self._alive(key):
            if create is None:
                return None
            self._data[key] = create()
        value = self._data[key]
        if not isinstance(value, kind):
            raise TypeError("WRONGTYPE Operation against a key holding the wrong kind of value")
        return value

    # ---- keys and strings
    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        with self._lock:
            exists = self._alive(key)
            if (nx and exists) or (xx and not exists):
                return None
            self._data[key] = str(value)
            self._expires.pop(key, None)
            if ex is not None:
                self._expires[key] = self.now() + ex
            elif px is not None:
                self._expires[key] = self.now() + px / 1000
            return True

    def get(self, key):
        with self._lock:
            return self._get_typed(key, str)

    def delete(self, *keys):
        with self._lock:
            removed = 0
            for key in keys:
                if self._alive(key):
                    del self._data[key]
                    self._expires.pop(key, None)
                    removed += 1
            return removed

    def exists(self, *keys):
        with self._lock:
            return sum(1 for key in keys if self._alive(key))

    def incr(self, key, amount=1):
        with self._lock:
            current = self._get_typed(key, str)
            try:
                value = int(current or 0) + amount
            except ValueError:
                raise ValueError("ERR value is not an integer or out of range") from None
            self._data[key] = str(value)
            return value

    def expire(self, key, seconds):
        with self._lock:
            if not self._alive(key):
                return False
            self._expires[key] = self.now() + seconds
            return True

    def ttl(self, key):
        with self._lock:
            if not self._alive(key):
                return -2
            deadline = self._expires.get(key)
            return -1 if deadline is None else math.ceil(deadline - self.now())

    def keys(self, pattern="*"):
        with self._lock:
            return sorted(k for k in list(self._data) if self._alive(k) and fnmatch.fnmatch(k, pattern))

    def flushall(self):
        with self._lock:
            self._data.clear()
            self._expires.clear()
            return True

    # ---- hashes
    def hset(self, key, field=None, value=None, mapping=None):
        with self._lock:
            h = self._get_typed(key, dict, create=dict)
            items = dict(mapping or {})
            if field is not None:
                items[field] = value
            added = sum(1 for f in items if f not in h)
            h.update({f: str(v) for f, v in items.items()})
            return added

    def hget(self, key, field):
        with self._lock:
            h = self._get_typed(key, dict)
            return None if h is None else h.get(field)

    def hgetall(self, key):
        with self._lock:
            return dict(self._get_typed(key, dict) or {})

    def hincrby(self, key, field, amount=1):
        with self._lock:
            h = self._get_typed(key, dict, create=dict)
            h[field] = str(int(h.get(field, 0)) + amount)
            return int(h[field])

    # ---- lists
    def lpush(self, key, *values):
        with self._lock:
            lst = self._get_typed(key, list, create=list)
            for v in values:
                lst.insert(0, str(v))
            return len(lst)

    def rpush(self, key, *values):
        with self._lock:
            lst = self._get_typed(key, list, create=list)
            lst.extend(str(v) for v in values)
            return len(lst)

    def lpop(self, key):
        with self._lock:
            lst = self._get_typed(key, list)
            return lst.pop(0) if lst else None

    def rpop(self, key):
        with self._lock:
            lst = self._get_typed(key, list)
            return lst.pop() if lst else None

    def llen(self, key):
        with self._lock:
            return len(self._get_typed(key, list) or [])

    def lrange(self, key, start, stop):
        with self._lock:
            lst = self._get_typed(key, list) or []
            stop = len(lst) if stop == -1 else stop + 1          # Redis ranges include the end index
            return lst[start:stop]

    # ---- sets
    def sadd(self, key, *members):
        with self._lock:
            s = self._get_typed(key, set, create=set)
            before = len(s)
            s.update(str(m) for m in members)
            return len(s) - before

    def srem(self, key, *members):
        with self._lock:
            s = self._get_typed(key, set) or set()
            removed = 0
            for m in members:
                if str(m) in s:
                    s.remove(str(m))
                    removed += 1
            return removed

    def smembers(self, key):
        with self._lock:
            return set(self._get_typed(key, set) or set())

    def sismember(self, key, member):
        with self._lock:
            return str(member) in (self._get_typed(key, set) or set())

    # ---- sorted sets
    def zadd(self, key, mapping):
        with self._lock:
            z = self._get_typed(key, _ZSet, create=_ZSet)
            added = sum(1 for m in mapping if m not in z)
            z.update({str(m): float(s) for m, s in mapping.items()})
            return added

    def zincrby(self, key, amount, member):
        with self._lock:
            z = self._get_typed(key, _ZSet, create=_ZSet)
            z[member] = z.get(member, 0.0) + amount
            return z[member]

    def zscore(self, key, member):
        with self._lock:
            return (self._get_typed(key, _ZSet) or {}).get(member)

    def zrange(self, key, start, stop, withscores=False, desc=False):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            ordered = sorted(z.items(), key=lambda kv: (kv[1], kv[0]), reverse=desc)
            stop = len(ordered) if stop == -1 else stop + 1
            chosen = ordered[start:stop]
            return chosen if withscores else [m for m, _ in chosen]

    def zrevrange(self, key, start, stop, withscores=False):
        return self.zrange(key, start, stop, withscores=withscores, desc=True)

    def zrem(self, key, *members):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            return sum(1 for m in members if z.pop(m, None) is not None)

    def zremrangebyscore(self, key, low, high):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            doomed = [m for m, score in z.items() if low <= score <= high]
            for m in doomed:
                del z[m]
            return len(doomed)

    def zcard(self, key):
        with self._lock:
            return len(self._get_typed(key, _ZSet) or {})


class _ZSet(dict):
    """member -> score."""
```

Let us try the commands. The clock is fake, so `ttl` is exact:

```python run
from miniredis import MiniRedis

clock = [1000.0]
r = MiniRedis(now=lambda: clock[0])

print("SET        ", r.set("greeting", "hello", ex=30))
print("GET        ", r.get("greeting"), "| TTL", r.ttl("greeting"))
print("SET NX     ", r.set("greeting", "other", nx=True), "<- None: the key already exists")
print("INCR       ", r.incr("visits"), r.incr("visits"), r.incr("visits", 10), "| TTL of a key without expiry:", r.ttl("visits"))
clock[0] += 31
print("after 31 s ", r.get("greeting"), "| TTL", r.ttl("greeting"), "<- -2 means 'does not exist'")

r.hset("session:abc", mapping={"user": "ada", "role": "customer"})
print("HGETALL    ", r.hgetall("session:abc"))
r.rpush("recent", "a", "b", "c")
r.lpush("recent", "z")
print("LRANGE     ", r.lrange("recent", 0, -1), "| LPOP", r.lpop("recent"), "| LLEN", r.llen("recent"))
r.sadd("tags", "red", "blue", "red")
print("SMEMBERS   ", sorted(r.smembers("tags")))
r.zadd("scores", {"ada": 120, "bo": 90})
r.zincrby("scores", 50, "bo")
print("ZREVRANGE  ", r.zrevrange("scores", 0, -1, withscores=True))
print("KEYS       ", r.keys("session:*"))
try:
    r.get("recent")
except TypeError as exc:
    print("wrong type ->", str(exc)[:30])
```
```text
SET         True
GET         hello | TTL 30
SET NX      None <- None: the key already exists
INCR        1 2 12 | TTL of a key without expiry: -1
after 31 s  None | TTL -2 <- -2 means 'does not exist'
HGETALL     {'user': 'ada', 'role': 'customer'}
LRANGE      ['z', 'a', 'b', 'c'] | LPOP z | LLEN 3
SMEMBERS    ['blue', 'red']
ZREVRANGE   [('bo', 140.0), ('ada', 120.0)]
KEYS        ['session:abc']
wrong type -> WRONGTYPE Operation against a 
```

> **Try it on your machine**: the same commands against a real Redis (needs Docker or a Redis install; not run here).
>
> ```bash
> docker run --rm -p 6379:6379 redis:7          # in one terminal
> docker exec -it <container-name> redis-cli    # in another
> ```
>
> Then type the commands. `redis-cli` prints replies in its own style: `OK` after `SET greeting hello EX 30`, `"hello"` for `GET greeting`, `(integer) 30` (or a little less) for `TTL greeting`, `(integer) 1`, `2`, `3` for the first `INCR visits` calls, and `(nil)` for a missing key. From Python:
>
> ```bash
> pip install redis
> python -c "import redis; r = redis.Redis(decode_responses=True); r.set('greeting', 'hello', ex=30); print(r.get('greeting'), r.ttl('greeting'))"
> ```
>
> Expected: `hello` and a TTL of `30` or `29`. Every example below works with `redis.Redis(decode_responses=True)` in place of `MiniRedis()`, because we only use commands that have the same names and return values. Container names, ports and exact TTL values on your machine will differ.

### Try it: why is `INCR` safe?

Two web servers each run `count = r.get("hits"); r.set("hits", int(count) + 1)`. What is wrong, and what is the one-command fix?

<details><summary>Answer</summary>

Read-modify-write across two commands: both servers read `41`, both write `42`, one increment is lost. `r.incr("hits")` is a single atomic command executed by Redis, so concurrent increments are all counted. The same reasoning applies to the `F()` expression in Django and to `UPDATE ... SET n = n + 1` in SQL.

</details>

## 4. Cache-aside in practice

### 4.1 The pattern

The most common way to use a cache is **cache-aside** (also called lazy loading): the application, not the cache, talks to the database.

1. Look in the cache. **Hit:** return it.
2. **Miss:** read from the database, store the result in the cache with a TTL, return it.
3. On a **write**, update the database and **delete** (or update) the cached copy (section 5).

Other patterns exist: **read-through** (the cache library loads missing values itself), **write-through** (writes go to the cache and the database together), and **write-behind** (writes go to the cache first and reach the database later, which is fast and risky, since a crash loses writes).

### 4.2 A product catalogue with a cache

```python
# catalog.py
import json
import random
import sqlite3

from fastapi import FastAPI, HTTPException

from miniredis import MiniRedis


class Catalog:
    """Products in SQLite, a cache in front of them. `db_reads` counts how often the database was really asked."""

    def __init__(self, cache: MiniRedis, ttl: int = 60):
        self.cache, self.ttl, self.db_reads = cache, ttl, 0
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER);
            INSERT INTO products VALUES (1, 'Keyboard', 4990), (2, 'Monitor', 18900), (3, 'USB cable', 350);
        """)

    @staticmethod
    def key(product_id: int) -> str:
        return f"product:v1:{product_id}"                       # namespace + version + id

    def _load(self, product_id: int):
        self.db_reads += 1
        row = self.db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None

    def get_product(self, product_id: int):
        cached = self.cache.get(self.key(product_id))
        if cached is not None:
            return json.loads(cached)                            # JSON, never pickle: the cache is outside our trust boundary
        product = self._load(product_id)
        ttl = self.ttl + random.randint(0, self.ttl // 10)       # a little jitter, so keys do not all expire together
        self.cache.set(self.key(product_id), json.dumps(product), ex=ttl)    # "null" is cached too (negative caching)
        return product

    def update_price(self, product_id: int, price_cents: int):
        self.db.execute("UPDATE products SET price_cents = ? WHERE id = ?", (price_cents, product_id))
        self.db.commit()
        self.cache.delete(self.key(product_id))                  # invalidate; the next read reloads


def build_app(catalog: Catalog) -> FastAPI:
    app = FastAPI()

    @app.get("/products/{product_id}")
    def read_product(product_id: int):
        product = catalog.get_product(product_id)
        if product is None:
            raise HTTPException(404, "product not found")
        return product

    return app
```

```python run
from fastapi.testclient import TestClient

from catalog import Catalog, build_app
from miniredis import MiniRedis

clock = [0.0]
cache = MiniRedis(now=lambda: clock[0])
catalog = Catalog(cache)
client = TestClient(build_app(catalog))

for _ in range(5):
    client.get("/products/1")
print("5 reads of product 1  -> database reads:", catalog.db_reads)

for _ in range(4):
    client.get("/products/99")                           # does not exist
print("4 reads of product 99 -> database reads:", catalog.db_reads, "(the 'not found' answer is cached too)")
print("status for 99         :", client.get("/products/99").status_code)

catalog.update_price(1, 3990)
print("after a price update  :", client.get("/products/1").json()["price_cents"], "| database reads:", catalog.db_reads)

clock[0] += 1000                                         # a long time passes: every entry expires
client.get("/products/1")
print("after the TTL         : database reads", catalog.db_reads, "| keys in cache:", cache.keys("product:*"))
```
```text
5 reads of product 1  -> database reads: 1
4 reads of product 99 -> database reads: 2 (the 'not found' answer is cached too)
status for 99         : 404
after a price update  : 3990 | database reads: 3
after the TTL         : database reads 4 | keys in cache: ['product:v1:1']
```

Points to notice:

- **Key design:** `product:v1:1` has a **namespace** (`product`), a **version** (`v1`) and the **id**. When you change the stored format, bump the version, and old entries are simply never read again. Never use a bare user-supplied string as a key.
- **JSON, not pickle.** Anything read from a shared cache is data from outside your process. Unpickling it is arbitrary code execution if an attacker can write to Redis (swe.07 section 14.7).
- **Negative caching:** the "not found" answer is stored (as `null`), so a client asking for product 99 a thousand times does not reach the database a thousand times. Give negative entries a **shorter** TTL in real systems, so a new product appears quickly.
- **TTL jitter:** adding a random 10% spreads expiry times, so thousands of keys loaded at once do not all expire at the same second (a "cache avalanche").
- **Invalidate on write:** `update_price` deletes the key; the next read reloads fresh data.

### 4.3 What to measure

Add counters for hits and misses and watch the **hit ratio**, the **latency** of hits and misses, and the **database load**. Without numbers you cannot tell a useful cache from a decoration. Two warnings: a cache with a near-zero hit ratio only adds latency and bugs, and a system that *needs* a warm cache to survive (the database cannot take the full traffic) will fall over when the cache is restarted. Plan for a cold cache (section 6).

### 4.4 The dangerous mistake: caching per-user data under a shared key

Suppose a "my recommendations" endpoint is slow, and a developer caches it. The key forgets who is asking:

```python run
import json

from fastapi import Depends, FastAPI, Header
from fastapi.testclient import TestClient

from miniredis import MiniRedis

cache = MiniRedis()
USERS = {"t-ada": "ada", "t-bo": "bo"}
HISTORY = {"ada": ["gardening books"], "bo": ["horror films"]}


def build_app(safe: bool) -> FastAPI:
    app = FastAPI()

    def current_user(authorization: str = Header(default="")):
        return USERS[authorization.removeprefix("Bearer ")]

    @app.get("/me/recommendations")
    def recommendations(user: str = Depends(current_user)):
        key = f"recs:{user}" if safe else "recs"                  # the bug: one shared key for everyone
        cached = cache.get(key)
        if cached is not None:
            return json.loads(cached)
        result = {"user": user, "items": HISTORY[user]}           # the "slow" per-user computation
        cache.set(key, json.dumps(result), ex=300)
        return result

    return app


for safe in (False, True):
    cache.flushall()
    c = TestClient(build_app(safe))
    ada = c.get("/me/recommendations", headers={"Authorization": "Bearer t-ada"}).json()
    bo = c.get("/me/recommendations", headers={"Authorization": "Bearer t-bo"}).json()
    print(f"safe={safe}: bo received {bo}")
```
```text
safe=False: bo received {'user': 'ada', 'items': ['gardening books']}
safe=True: bo received {'user': 'bo', 'items': ['horror films']}
```

With the shared key, **bo receives ada's private data**: a data leak caused by a performance optimisation. The same bug appears at every layer: a CDN or proxy caching a personalised page for everybody. Rules:

1. Anything that depends on the caller (user id, role, language, tenant, permissions) belongs **in the key**, or must not be cached.
2. For HTTP caches (browser, CDN), mark personal responses `Cache-Control: private` (or `no-store` for sensitive ones), and use the `Vary` header when the response depends on a request header (`Vary: Accept-Language`).
3. **Never cache the result of an authorisation decision** for longer than you can afford a wrong answer: a user whose access was removed should not keep access for the length of a TTL.
4. Write a **two-user test** (swe.07 section 8.4) for every cached personalised endpoint.

### Try it: key design

You cache search results for `GET /search?q=...&page=...&sort=...` for logged-in users, where results depend on the user's region. Write the cache key.

<details><summary>Answer</summary>

Something like `search:v2:{region}:{sort}:{page}:{sha256(normalised q)}`. It includes everything that changes the answer (region, sort, page, the query), a version, and a hash of the query so that long or odd user text cannot create enormous or malicious keys. It does not include the user id because the results depend only on region, which makes the cache shared by everyone in that region. If results also depended on permissions, the permission set (or user id) would be part of the key.

</details>

### Try it: why the 404 is cached

Why does the demo cache "product not found"? What is the risk, and what do you do about it?

<details><summary>Answer</summary>

Requests for ids that do not exist (typos, scanners, attackers walking ids) would otherwise reach the database every time ("cache penetration"). The risk is that when the product is created later, the cached "not found" hides it until the TTL ends. Fix: give negative entries a short TTL (say 10 to 30 seconds) and delete the key when a product is created.

</details>


## 5. Cache invalidation

> "There are only two hard things in computer science: cache invalidation and naming things." (a well-known joke, and a true one.)

### 5.1 The problem

A cache is a **copy**. When the original changes, the copy is wrong until someone fixes it. You have four basic strategies, and real systems combine them:

| Strategy | How | Staleness | Cost / risk |
|---|---|---|---|
| **TTL only** | let entries expire | up to the TTL | simplest; stale for as long as the TTL says |
| **Delete on write** | the writer deletes the key after changing the database | small, but see 5.2 | needs every write path to remember |
| **Update on write** (write-through) | the writer also stores the new value | small | the writer must produce the cached form |
| **Versioned or immutable keys** | the key contains a version or a content hash; changing data means a new key | none for readers of the new key | old keys linger until they expire |

Whatever you choose, keep a **TTL as a backstop**. If an invalidation bug leaves bad data behind, the TTL limits how long it can live.

### 5.2 The classic race: "delete after write" is not enough

Look at the delete-on-write pattern from section 4. A reader that misses loads from the database and then stores the result. A writer updates the database and deletes the key. What if they overlap?

```text
   reader                                  writer
   ------                                  ------
   miss; read the database -> OLD
                                           update the database -> NEW
                                           delete the cache key
   store OLD in the cache      <-- the cache now holds the old value until its TTL ends
```

No error, no log line: the cache is silently wrong. Rare races like this happen all the time at scale. We can check every possible interleaving with a few lines of code. Each actor is a list of steps; we run every way of mixing the two lists (each list keeping its own order) and see which ones leave the cache stale:

```python run
from itertools import combinations

from miniredis import MiniRedis


def interleavings(a, b):
    """Every way to merge two step lists, keeping the order inside each list."""
    n = len(a) + len(b)
    for positions in combinations(range(n), len(a)):
        merged, ia, ib = [], iter(a), iter(b)
        for i in range(n):
            merged.append(next(ia) if i in positions else next(ib))
        yield merged


def run_scheme(reader_steps, writer_steps, fresh_read):
    stale = []
    for order in interleavings(reader_steps, writer_steps):
        world = {"db": "OLD", "cache": MiniRedis(), "local": {}}
        for step in order:
            step(world)
        if fresh_read(world) != "NEW":
            stale.append([step.__name__ for step in order])
    return stale


# ---- scheme 1: the writer updates the database, then deletes the key
def r_read_db(w): w["local"]["v"] = w["db"]
def r_store(w): w["cache"].set("p", w["local"]["v"])
def w_update(w): w["db"] = "NEW"
def w_delete(w): w["cache"].delete("p")

def fresh_read_plain(w):
    return w["cache"].get("p") or w["db"]                 # a later reader: cache first, database on a miss

bad = run_scheme([r_read_db, r_store], [w_update, w_delete], fresh_read_plain)
print(f"delete-on-write: {len(bad)} of 6 interleavings leave stale data")
for order in bad:
    print("   ", " -> ".join(order))


# ---- scheme 2: a generation number is part of the key; the writer bumps it AFTER updating the database
def r_read_gen(w): w["local"]["gen"] = w["cache"].get("gen") or "0"
def r_read_db2(w): w["local"]["v"] = w["db"]
def r_store2(w): w["cache"].set(f"p:{w['local']['gen']}", w["local"]["v"])
def w_update2(w): w["db"] = "NEW"
def w_bump(w): w["cache"].incr("gen")

def fresh_read_gen(w):
    gen = w["cache"].get("gen") or "0"
    return w["cache"].get(f"p:{gen}") or w["db"]

bad = run_scheme([r_read_gen, r_read_db2, r_store2], [w_update2, w_bump], fresh_read_gen)
print(f"generation key : {len(bad)} of 10 interleavings leave stale data")
```
```text
delete-on-write: 1 of 6 interleavings leave stale data
    r_read_db -> w_update -> w_delete -> r_store
generation key : 0 of 10 interleavings leave stale data
```

Study the second scheme, because the same idea fixes many races. The reader **reads the generation first**, then the database, and stores under the generation it started with. If a writer changes the data in the meantime, the reader's late store goes into the *old* generation's key, which nobody reads any more. The writer's order matters: **update the database first, then bump the generation**. A model-checking script like this one is worth keeping in your toolbox for any "can these two things interleave badly?" question.

Practical consequences:

- Keep TTLs short enough that a missed invalidation heals itself.
- For the strongest guarantee, put a **version number** in the database row, in the cached value, and let the cache accept only newer versions (this needs an atomic compare-and-set, which Redis offers through Lua scripts or `WATCH`).
- Accept that a cache gives **eventual** consistency, and decide per data type how stale is acceptable.

### 5.3 More tools

- **Write-through / update on write:** the writer stores the new value itself, so readers never see a gap. Beware two writers racing (the same interleaving problem).
- **Event-based invalidation:** when data changes, publish an event ("product 1 changed"); every application instance drops its local copy. Redis pub/sub or a message queue carries the event. Events can be lost, so keep the TTL.
- **Tag-based invalidation:** store the keys that belong to a group in a set (`tag:category:5` holds `product:v1:1`, `product:v1:2`), and delete the whole group when the category changes.
- **Immutable keys:** cache by content hash or by version (`/static/app.3f9a1c.js`, `report:2026-10:v3`). Nothing ever needs invalidating, because changed content has a new key.
- **Stale-while-revalidate:** serve the old value immediately while one request refreshes it in the background (section 6).
- **Conditional HTTP requests:** browsers and CDNs can ask "has this changed?" with `If-None-Match: <etag>` and get `304 Not Modified` with no body (the read-side partner of the `If-Match` header of swe.07 section 12.6).

### 5.4 Decide a staleness budget

For each kind of data, write down how stale it may be. It makes design decisions concrete:

| Data | Staleness budget | Approach |
|---|---|---|
| marketing text | an hour | TTL only |
| product price shown in the catalogue | a minute | TTL 60 s + delete on write |
| price used to charge the customer | none | read from the database at checkout |
| stock count on a product page | 30 seconds ("only 3 left" may lag) | TTL; the order itself checks the database |
| user permissions | a few seconds at most | very short TTL, or no cache, plus delete on change |
| leaderboard | 5 seconds | TTL or periodic rebuild |

### Try it: what is wrong with this write path?

```python
def update_price(pid, cents):
    cache.delete(f"product:{pid}")
    db.execute("UPDATE products SET price_cents=? WHERE id=?", (cents, pid))
```

<details><summary>Answer</summary>

It deletes the cache **before** the database changes. A reader arriving between the two lines misses, reads the *old* price from the database and caches it, and the update that follows never invalidates it, so the old price lives until the TTL. Always change the source of truth first, then invalidate (and prefer the generation or version technique above if the race matters).

</details>

### Try it: choose the budget

A teacher dashboard shows each student's current grade and is cached for 5 minutes. A teacher corrects a grade and immediately reloads the page, still sees the old grade, and files a bug. What are two reasonable fixes?

<details><summary>Answer</summary>

(1) Delete (or overwrite) the cached entry in the same code path that saves the corrected grade, so the teacher sees their own change at once ("read your own writes"). (2) Shorten the TTL for this data, or show the cached value with an "updated 3 minutes ago" label. The teacher's expectation ("I changed it, so I should see it") is a real requirement; satisfy it for the person who made the change, even if other viewers may lag a little.

</details>

## 6. Cache stampedes, avalanches and hot keys

### 6.1 The stampede

A **stampede** (or "thundering herd", or "dog-pile") happens when a popular key expires and many requests miss **at the same moment**. All of them go to the database, which is slow because it is overloaded, which keeps the key missing for longer, which brings more requests. Let us measure it. 20 threads ask for the same key at once; loading takes 50 ms:

```python
# stampede.py
import json
import threading
import time


class Loader:
    """A slow, counted data source (the database)."""

    def __init__(self, delay=0.05):
        self.delay, self.calls, self._lock = delay, 0, threading.Lock()

    def __call__(self, key):
        with self._lock:
            self.calls += 1
        time.sleep(self.delay)
        return {"key": key, "value": 42}


def get_naive(cache, key, loader, ttl=60):
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    value = loader(key)                                       # every concurrent miss lands here
    cache.set(key, json.dumps(value), ex=ttl)
    return value


def get_single_flight(cache, key, loader, ttl=60, lock_ttl=10, poll=0.005, timeout=5.0):
    """Only one caller loads; the others wait for its result."""
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    if cache.set(f"lock:{key}", "1", ex=lock_ttl, nx=True):          # I won the right to load
        try:
            value = loader(key)
            cache.set(key, json.dumps(value), ex=ttl)
            return value
        finally:
            cache.delete(f"lock:{key}")
    deadline = time.monotonic() + timeout                           # somebody else is loading: wait for the value
    while time.monotonic() < deadline:
        cached = cache.get(key)
        if cached is not None:
            return json.loads(cached)
        time.sleep(poll)
    return loader(key)                                              # the loader died or is too slow: do it ourselves


def run_concurrently(fn, n=20):
    gate, results = threading.Barrier(n), []

    def worker():
        gate.wait()                                                 # all threads start at the same instant
        results.append(fn())

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
```

```python run
from miniredis import MiniRedis
from stampede import Loader, get_naive, get_single_flight, run_concurrently

for name, getter in (("naive", get_naive), ("single flight", get_single_flight)):
    cache, loader = MiniRedis(), Loader()
    results = run_concurrently(lambda: getter(cache, "hot", loader))
    print(f"{name:14} 20 simultaneous misses -> database loads: {'many' if loader.calls > 1 else loader.calls}"
          f" | all 20 callers got an answer: {len(results) == 20 and all(r['value'] == 42 for r in results)}")
```
```text
naive          20 simultaneous misses -> database loads: many | all 20 callers got an answer: True
single flight  20 simultaneous misses -> database loads: 1 | all 20 callers got an answer: True
```

The naive version hammers the database with (nearly) one load per caller. **Single flight** lets exactly one caller load, using `SET key value NX EX` as a lock; the others poll the cache for the result. (The exact count in the naive case varies with scheduling, usually close to 20, which is why the output says "many".) Note the safety net: if the loading caller dies, its lock expires (`lock_ttl`) and waiters fall back to loading themselves instead of hanging.

### 6.2 More defences

| Technique | Idea | Trade-off |
|---|---|---|
| **Single flight** (above) | one loader, the rest wait | waiting adds latency; needs a lock |
| **In-process coalescing** | one lock per key *inside each process* | cheap; N processes still send N loads |
| **Stale-while-revalidate** | keep the value past its "soft" expiry; one request refreshes it while everyone else gets the stale value instantly | users may see slightly old data |
| **Early (probabilistic) refresh** | each request near the expiry refreshes with rising probability, so the key is renewed *before* it expires | a bit of extra work |
| **TTL jitter** | random +/- 10% on every TTL | prevents mass expiry |
| **Pre-warming** | load the hot keys at start-up or deploy | needs a list of hot keys |

Here is stale-while-revalidate: the entry carries a **soft** deadline for "refresh me" and lives on until a later **hard** deadline:

```python run
import json

from miniredis import MiniRedis
from stampede import Loader

clock = [0.0]
cache = MiniRedis(now=lambda: clock[0])
loader = Loader(delay=0)


def get_swr(key, soft=60, hard=600):
    raw = cache.get(key)
    if raw is not None:
        entry = json.loads(raw)
        if entry["soft_expires"] > clock[0]:
            return entry["value"], "fresh"
        if cache.set(f"lock:{key}", "1", ex=10, nx=True):          # exactly one request refreshes...
            entry = {"value": loader(key), "soft_expires": clock[0] + soft}
            cache.set(key, json.dumps(entry), ex=hard)
            cache.delete(f"lock:{key}")
            return entry["value"], "refreshed by me"
        return entry["value"], "stale, served instantly"           # ...everyone else gets the old value without waiting
    entry = {"value": loader(key), "soft_expires": clock[0] + soft}
    cache.set(key, json.dumps(entry), ex=hard)
    return entry["value"], "cold miss"


print(get_swr("k")[1])                   # cold miss
clock[0] += 30
print(get_swr("k")[1])                   # still fresh
clock[0] += 40                           # past the soft deadline (70 s)
cache.set("lock:k", "1", ex=10)          # pretend another request is already refreshing
print(get_swr("k")[1])                   # stale, served instantly
cache.delete("lock:k")
print(get_swr("k")[1], "| database loads so far:", loader.calls)
```
```text
cold miss
fresh
stale, served instantly
refreshed by me | database loads so far: 2
```

### 6.3 Related names

- **Cache avalanche:** many keys expire together (a cache restart, or a batch loaded at the same second), and the database sees a wall of misses. Defence: TTL jitter, staggered warming, a cache that survives restarts, and protecting the database with limits.
- **Cache penetration:** requests for keys that can never exist always miss (see negative caching in 4.2). Defence: negative entries with short TTLs, input validation, and rate limits. A Bloom filter of valid ids is the heavy-duty version.
- **Hot key:** one key gets so much traffic that its single Redis node becomes the bottleneck. Defence: a small in-process cache in front (even a 1-second TTL removes 99% of the load), or replicate the key under several names and pick one at random.
- **Big keys:** a 50 MB value blocks Redis while it is copied, delaying everyone. Keep values small; split lists.

### Try it: count the loads

200 requests per second hit a key whose loader takes 100 ms. The key expires. Without protection, roughly how many loads start before the first one finishes? With single flight?

<details><summary>Answer</summary>

About 20: during the 100 ms the first load runs, 0.1 s x 200 requests/s = 20 more requests miss and each starts its own load (and the database slows down, so the window grows and more pile in). With single flight it is exactly one load; the 20 waiting requests get the result when it finishes. This is also a Little's-law calculation (section 15): requests in flight = arrival rate x time in the system.

</details>

## 7. Other jobs for Redis: sessions, counters, locks, events

### 7.1 Sessions

In swe.07 section 3 the session store was a Python dictionary. A real deployment has several web servers, so sessions must live in a **shared** store with automatic expiry, and Redis is the usual place. A session is a small hash; the key is the **hash of the session id** (so a leaked Redis dump cannot be turned into cookies); `EXPIRE` gives the idle timeout, and a stored `created` time gives the absolute timeout:

```python run
import hashlib
import secrets

from miniredis import MiniRedis


class RedisSessions:
    def __init__(self, redis, idle=1800, absolute=43200, now=None):
        self.r, self.idle, self.absolute, self.now = redis, idle, absolute, now or redis.now

    @staticmethod
    def _key(sid):
        return "session:" + hashlib.sha256(sid.encode()).hexdigest()

    def create(self, user_id):
        sid = secrets.token_urlsafe(32)
        self.r.hset(self._key(sid), mapping={"user": user_id, "created": int(self.now())})
        self.r.expire(self._key(sid), self.idle)
        self.r.sadd(f"user_sessions:{user_id}", self._key(sid))             # lets us log a user out everywhere
        return sid

    def get(self, sid):
        key = self._key(sid)
        data = self.r.hgetall(key)
        if not data:
            return None
        if self.now() - int(data["created"]) > self.absolute:               # absolute timeout
            self.destroy(sid)
            return None
        self.r.expire(key, self.idle)                                        # sliding idle timeout
        return data["user"]

    def destroy(self, sid):
        key = self._key(sid)
        user = self.r.hget(key, "user")
        self.r.delete(key)
        if user:
            self.r.srem(f"user_sessions:{user}", key)

    def destroy_all(self, user_id):
        for key in self.r.smembers(f"user_sessions:{user_id}"):
            self.r.delete(key)
        self.r.delete(f"user_sessions:{user_id}")


clock = [0.0]
sessions = RedisSessions(MiniRedis(now=lambda: clock[0]))
s1, s2 = sessions.create("ada"), sessions.create("ada")
print("valid         :", sessions.get(s1))
clock[0] += 1700
print("active at 1700s:", sessions.get(s1), "(idle timer renewed)")
clock[0] += 1700
print("idle again     :", sessions.get(s1), "| the untouched one:", sessions.get(s2), "<- expired by Redis")
clock[0] += 30000
sessions2 = sessions.create("ada")
sessions.destroy_all("ada")
print("after logout everywhere:", sessions.get(sessions2))
```
```text
valid         : ada
active at 1700s: ada (idle timer renewed)
idle again     : ada | the untouched one: None <- expired by Redis
after logout everywhere: None
```

Redis is a good fit for sessions because they are small, short-lived and read on every request. The caveat from swe.07 section 3 remains: the cookie flags (`HttpOnly`, `Secure`, `SameSite`) and a **new id at login** matter more than where the data lives. Also decide what happens if Redis restarts and loses sessions: users log in again, which is acceptable for most sites.

### 7.2 Shared rate limits

The in-memory limiter of swe.07 section 11 is wrong behind several workers. With a shared store, the simplest algorithm is a **fixed window counter**: `INCR` a key named after the window, and `EXPIRE` it. The detail that bites is **the gap between the two commands**:

```python run
from miniredis import MiniRedis


def hit_unsafe(r, user, window, now):
    key = f"rate:{user}:{int(now() // window)}"
    count = r.incr(key)                                    # (1) increment
    # ... the process crashes or is killed HERE, before the next line ...
    if count == 1:
        r.expire(key, window)                              # (2) set the expiry
    return count


def hit_safe(r, user, window, now):
    key = f"rate:{user}:{int(now() // window)}"
    r.set(key, 0, ex=window, nx=True)                      # create-with-expiry first, in ONE atomic command
    return r.incr(key)                                     # INCR keeps the existing TTL


clock = [100.0]
r = MiniRedis(now=lambda: clock[0])
hit_unsafe(r, "ada", 60, lambda: clock[0])                 # the first call "crashes" before expire(); simulate by deleting TTL
r._expires.pop("rate:ada:1", None)
clock[0] += 10_000
print("unsafe: the counter survives for ever, TTL =", r.ttl("rate:ada:1"), "-> the window key never resets")

r2 = MiniRedis(now=lambda: clock[0])
for _ in range(3):
    hit_safe(r2, "ada", 60, lambda: clock[0])
window_key = f"rate:ada:{int(clock[0] // 60)}"
print("safe  : count", r2.get(window_key), "| TTL", r2.ttl(window_key), "seconds, set by the first command")
```
```text
unsafe: the counter survives for ever, TTL = -1 -> the window key never resets
safe  : count 3 | TTL 60 seconds, set by the first command
```

(In the unsafe version the window key name includes the window number, so a "never expires" key is merely a memory leak; if you use a fixed key such as `rate:ada` the user is blocked **for ever**.) In real Redis you would do both steps in a **Lua script** or a pipeline with `MULTI/EXEC` so that they cannot be separated; the `SET ... NX EX` trick above achieves the same for this counter.

A **sliding-window log** uses a sorted set whose scores are timestamps: add the current time, remove entries older than the window (`ZREMRANGEBYSCORE`), and count what is left (`ZCARD`). The count is exact, at the cost of memory proportional to the limit:

```python run
from miniredis import MiniRedis

clock = [0.0]
r = MiniRedis(now=lambda: clock[0])


def allow(user, limit=3, window=10):
    key = f"rate:log:{user}"
    now = clock[0]
    r.zremrangebyscore(key, 0, now - window)               # forget requests older than the window
    if r.zcard(key) >= limit:
        return False
    r.zadd(key, {f"{now}:{r.zcard(key)}": now})            # the member must be unique per request
    r.expire(key, window)
    return True


results = []
for t in (0, 1, 2, 3, 9, 10.5, 11.5, 12.5):
    clock[0] = t
    results.append((t, allow("ada")))
print(results)
```
```text
[(0, True), (1, True), (2, True), (3, False), (9, False), (10.5, True), (11.5, True), (12.5, True)]
```

In a real system these check-then-add steps must be **atomic** (a Lua script), otherwise two servers can both see "2 of 3 used" and both add one. That atomicity requirement is the reason Lua scripting exists in Redis.

### 7.3 Distributed locks, and why they are dangerous

Sometimes only one process may do something at a time (rebuild a report, run the nightly job). The Redis recipe is `SET lock:name <token> NX PX 30000`: set the key only if it does not exist, with an expiry so that a crashed holder cannot block everyone for ever. The classic mistakes show up as soon as time passes:

```python run
from miniredis import MiniRedis

clock = [0.0]
r = MiniRedis(now=lambda: clock[0])
LOCK = "lock:report"


def acquire(token, ttl=10):
    return bool(r.set(LOCK, token, ex=ttl, nx=True))


def release_naive(token):
    r.delete(LOCK)                                          # BUG: deletes whoever holds the lock now


def release_safe(token):
    # compare-and-delete must be ONE atomic step; in real Redis this is a small Lua script:
    #   if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end
    with r._lock:
        if r.get(LOCK) == token:
            r.delete(LOCK)


for release in (release_naive, release_safe):
    r.flushall()
    clock[0] = 0.0
    print(f"--- {release.__name__} ---")
    print("A acquires        :", acquire("A"))
    clock[0] = 15.0                                         # A is slow (a long garbage collection, a stalled network): its lock expired
    print("B acquires        :", acquire("B"), "(A's lock had expired)")
    release("A")                                            # A wakes up and releases "its" lock
    print("C acquires        :", acquire("C"), "<- should be False: B still holds the lock")
```
```text
--- release_naive ---
A acquires        : True
B acquires        : True (A's lock had expired)
C acquires        : True <- should be False: B still holds the lock
--- release_safe ---
A acquires        : True
B acquires        : True (A's lock had expired)
C acquires        : False <- should be False: B still holds the lock
```

With the naive release, A deletes **B's** lock, and C walks in while B is working: two holders at once. Always store a unique **token** and delete only if the token matches.

Even the safe version cannot promise mutual exclusion: A believed it still held the lock after it expired (it was just paused), and may still *write* to the shared resource. The robust fix is a **fencing token**: every lock grant returns an increasing number, and the resource rejects writes carrying an older number than one it has already seen.

```python run
from miniredis import MiniRedis

r = MiniRedis()


class Storage:
    """The protected resource: it remembers the highest fencing token it has seen."""
    def __init__(self):
        self.highest, self.value = 0, None

    def write(self, token, value):
        if token < self.highest:
            return "REJECTED (stale lock holder)"
        self.highest, self.value = token, value
        return "ok"


storage = Storage()
token_a = r.incr("lock:report:fence")           # A is granted the lock with token 1
token_b = r.incr("lock:report:fence")           # A's lock expires; B is granted it with token 2
print("B writes:", storage.write(token_b, "from B"))
print("A (paused, now awake) writes:", storage.write(token_a, "from A"))
print("final value:", storage.value)
```
```text
B writes: ok
A (paused, now awake) writes: REJECTED (stale lock holder)
final value: from B
```

Take-aways: a Redis lock is an **efficiency** tool (it avoids doing the same work twice, mostly) and not a **correctness** guarantee. When correctness matters (money, stock), rely on database transactions, unique constraints, conditional updates and fencing tokens, as in swe.07 section 13. People argue about multi-node "Redlock" for years; the safe attitude is: do not build correctness on timing assumptions.

### 7.4 Pub/sub, streams and leaderboards

- **Pub/sub** (`PUBLISH`, `SUBSCRIBE`) is fire-and-forget: a message goes to the subscribers connected *right now*, and is gone. A subscriber that was offline never sees it. It suits live notifications and cache-invalidation hints, never jobs that must not be lost.
- **Streams** (`XADD`, consumer groups) are Redis's durable log with acknowledgements, the nearest Redis feature to a real message queue. Task libraries use lists or streams, not pub/sub.
- **Sorted sets** make leaderboards trivial: `ZINCRBY scores 10 ada`, then `ZREVRANGE scores 0 9 WITHSCORES` for the top ten, in logarithmic time, as the section 3.2 demo showed.

### Try it: spot the lock bug

```python
if r.set("lock:nightly", "1", nx=True):
    run_nightly_job()
    r.delete("lock:nightly")
```

Name two problems.

<details><summary>Answer</summary>

(1) No expiry: if the process crashes during `run_nightly_job()`, the lock stays for ever and the job never runs again. Add `ex=` longer than the job's normal duration. (2) The value is a constant, so if the lock expired and another process took it, the `delete` removes *their* lock. Use a random token and compare before deleting. Also consider an exception in `run_nightly_job()` (use `try/finally`) and whether the job itself should be idempotent, since the lock can never promise exclusivity.

</details>

### Try it: choose the structure

Pick a Redis structure for: (a) "how many times has this IP called the login endpoint in the last minute"; (b) the 100 most recent search terms; (c) the set of users currently online; (d) a user profile with 6 fields that you update one field at a time.

<details><summary>Answer</summary>

(a) A string counter with `INCR` and a TTL (or a sorted set for an exact sliding window). (b) A list: `LPUSH` the new term, `LTRIM` to 100, `LRANGE` to read. (c) A set (`SADD`/`SREM`/`SISMEMBER`), with a TTL on per-user "heartbeat" keys if users can vanish without logging out. (d) A hash: `HSET profile:7 city Oslo` changes one field without rewriting the whole object.

</details>


## 8. Queues and background work: the ideas

### 8.1 Vocabulary

| Word | Meaning |
|---|---|
| **Producer** | code that creates a job and **enqueues** it (usually the web app) |
| **Queue** | the waiting line of jobs |
| **Broker** | the system that stores the queue (Redis, RabbitMQ, SQS, a database table) |
| **Worker / consumer** | a separate process that takes jobs from the queue and runs them |
| **Job / task / message** | one unit of work: a **kind** (what to do) plus a **payload** (the data it needs) |
| **Ack** (acknowledge) | the worker tells the broker "this job is finished; forget it" |
| **Result backend** | optional place where results or status are stored |
| **Dead-letter queue (DLQ)** | where jobs go after failing too many times, for a human to inspect |

The usual shape is a **work queue** with competing consumers: any number of workers take jobs from the same queue, each job goes to one worker, and you add workers to add capacity. This is different from **publish/subscribe**, where one message is copied to every subscriber.

### 8.2 What belongs in a job

Move work out of the request when it is **slow** (reports, video, large imports), **unreliable** (external APIs, e-mail), or a **side effect** that the user does not need to wait for (receipt, analytics, search-index update). Keep in the request whatever the user needs **now** and whatever must be **atomic** with the main action.

The pattern for the web side is `202 Accepted`: "I took your request; here is where to check on it."

```python run
import sqlite3

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
jobs = sqlite3.connect(":memory:", check_same_thread=False)
jobs.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, kind TEXT, state TEXT)")


@app.post("/reports", status_code=202)
def request_report():
    cur = jobs.execute("INSERT INTO jobs (kind, state) VALUES ('monthly-report', 'queued')")
    jobs.commit()
    return {"job_id": cur.lastrowid, "status_url": f"/reports/{cur.lastrowid}"}          # answer immediately


@app.get("/reports/{job_id}")
def report_status(job_id: int):
    row = jobs.execute("SELECT state FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return {"job_id": job_id, "state": row[0]}


c = TestClient(app)
r = c.post("/reports")
print(r.status_code, r.json())
print(c.get(r.json()["status_url"]).json())
```
```text
202 {'job_id': 1, 'status_url': '/reports/1'}
{'job_id': 1, 'state': 'queued'}
```

The client then polls the status URL, receives a notification (WebSocket, push, e-mail), or is simply told "we will e-mail you". Rule of thumb: **never make the user wait for something you can promise to do reliably later**, and make that promise reliable (the rest of this chapter).

### 8.3 `BackgroundTasks` is not a queue

FastAPI's `BackgroundTasks` (swe.05 section 14) and Flask's threads run the work **inside the web process**, after the response. That is fine for tiny, losable work (a log line). It has no storage, so a restart or crash **loses** pending tasks; no retries; no visibility; the web process shares CPU and memory with the work. A real queue stores jobs **outside** the process that created them.

### 8.4 Delivery guarantees

The most important thing to understand about queues is *when the job is acknowledged*, because a worker can crash at any moment. A worker's life for one job has three moments: **receive** it, **do the work** (the effect), **ack** it. If the process dies, the broker only knows whether the ack arrived.

```python run
def simulate(ack_first: bool, crash_at: str):
    """One job, one worker, a crash at a chosen moment. Returns what the outside world saw."""
    broker = {"pending": ["send-email"], "effects": 0}

    def attempt(crash_here):
        job = broker["pending"][0] if broker["pending"] else None
        if job is None:
            return
        if ack_first:
            broker["pending"].remove(job)                    # ack immediately: the broker forgets the job
        if crash_here == "before-effect":
            return                                           # the process dies
        broker["effects"] += 1                               # the e-mail is sent
        if crash_here == "after-effect":
            return                                           # dies before the ack (or after, if ack_first)
        if not ack_first:
            broker["pending"].remove(job)                    # ack after the work

    attempt(crash_at)                                        # first attempt crashes
    attempt(None)                                            # the worker restarts and tries again, if there is anything left
    return broker["effects"]


print(f"{'ack timing':16} {'crash point':14} effects (e-mails sent)")
for ack_first in (True, False):
    for crash in ("before-effect", "after-effect"):
        n = simulate(ack_first, crash)
        verdict = "LOST" if n == 0 else "DUPLICATE" if n > 1 else "ok"
        print(f"{'ack first' if ack_first else 'ack after work':16} {crash:14} {n}  {verdict}")
```
```text
ack timing       crash point    effects (e-mails sent)
ack first        before-effect  0  LOST
ack first        after-effect   1  ok
ack after work   before-effect  1  ok
ack after work   after-effect   2  DUPLICATE
```

| Guarantee | How | What a crash can do | Example |
|---|---|---|---|
| **At most once** | ack **before** the work | the job may be **lost** | losing a metric sample is fine |
| **At least once** | ack **after** the work | the job may run **twice** | the default for serious systems |
| **Exactly once** | not achievable as *delivery* between independent systems | n/a | what people want |

Exactly-once *delivery* is impossible in general: the worker cannot atomically "do an effect in the outside world" and "tell the broker", so one of the two always happens first. What you can build is **effectively once**: use **at-least-once** delivery and make the work **idempotent**, so a second run changes nothing. That is the central skill of this chapter (section 11). Most queues, including the one we build next, provide at-least-once.

### 8.5 Choosing a broker

| Broker | Strengths | Watch out for |
|---|---|---|
| **Redis** (lists or streams) | very fast, simple, already there for caching; used by RQ, arq, Celery | memory-bound; persistence settings decide what a crash loses |
| **RabbitMQ** | a real message broker: routing, acks, dead-letter exchanges, priorities; Celery's classic choice | one more service to run |
| **Amazon SQS** and cloud queues | managed, durable, scales without work | visibility-timeout rules, ordering limits, cost per request |
| **Kafka** | a durable **log** for high-volume event streams and replay | not a simple job queue |
| **A database table** (PostgreSQL, even SQLite) | the job commits **in the same transaction** as your business data; nothing extra to run; easy to inspect | polling load; throughput limit in the thousands per second |

Do not reach for a broker because it sounds professional. A database-backed queue is a perfectly good choice for many systems, and it is the one we **build** here, because it makes every rule visible.

### Try it: pick the guarantee

Choose at-most-once or at-least-once: (a) incrementing a page-view counter in a statistics job; (b) "charge the customer's card"; (c) sending a password-reset e-mail.

<details><summary>Answer</summary>

(a) At-most-once is acceptable: losing one count in a million is fine, and duplicates would inflate the numbers. (b) At-least-once, plus idempotency (the payment provider's idempotency key): a lost charge means unpaid goods, a duplicate means an angry customer; only "effectively once" is acceptable. (c) At-least-once is the sensible choice: a lost e-mail makes the user retry, a duplicate is mildly annoying (and harmless, since the old token is replaced). Unlike (b), a duplicate costs little here.

</details>

## 9. Building a durable job queue

To understand queue systems, we build one on SQLite. It has every feature that matters: durable storage, **leases** (so a crashed worker's job comes back), retries with delays, a dead-letter state, duplicate-prevention keys and statistics. The ideas map directly to Celery, RQ, SQS and the PostgreSQL queue libraries.

### 9.1 The table

A job is a row. Its **state** moves like this:

```text
                 enqueue
                    |
                    v
   +---------> queued  --reserve--> running --complete--> done
   |            ^   (run_at <= now)    |  |
   |            |                      |  +--fail, attempts left--> queued (later run_at = backoff)
   |            +--lease expired-------+
   |                                   +--fail permanently, or attempts used up--> dead
   +-- requeue_dead (an operator, after fixing the cause) -----------------------<
```

The key idea is the **lease**. When a worker reserves a job, it gets it only until `lease_until`. If the worker finishes, it completes the job. If the worker crashes (or hangs), nobody tells the queue, but the lease **runs out**, and the job becomes available to another worker. This is the "visibility timeout" of Amazon SQS, and the reason the guarantee is **at least once**.

### 9.2 The queue

```python
# jobqueue.py
import json
import sqlite3
import time
from contextlib import closing

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    queue        TEXT    NOT NULL DEFAULT 'default',
    kind         TEXT    NOT NULL,
    payload      TEXT    NOT NULL,
    dedupe_key   TEXT    UNIQUE,                       -- two enqueues with the same key make one job
    state        TEXT    NOT NULL DEFAULT 'queued' CHECK (state IN ('queued', 'running', 'done', 'dead')),
    attempts     INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    run_at       REAL    NOT NULL,                     -- not before this time (delays and backoff)
    lease_until  REAL,                                 -- while running: the lease deadline
    worker       TEXT,                                 -- who holds the lease
    last_error   TEXT,
    created_at   REAL    NOT NULL,
    finished_at  REAL
);
CREATE INDEX IF NOT EXISTS jobs_ready ON jobs (queue, state, run_at);
"""


class JobQueue:
    def __init__(self, path: str, now=time.time):
        self.path, self.now = path, now
        with closing(self._connect()) as db:
            db.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)       # autocommit: each statement is atomic
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode = WAL")                                  # readers do not block the writer
        db.execute("PRAGMA busy_timeout = 10000")
        return db

    # ---- producer side
    def enqueue(self, kind, payload, **options) -> int:
        with closing(self._connect()) as db:
            return self.enqueue_in(db, kind, payload, **options)

    def enqueue_in(self, db, kind, payload, *, queue="default", delay=0.0, max_attempts=5, dedupe_key=None) -> int:
        """Enqueue using the CALLER's connection: the job commits or rolls back together with the caller's own data."""
        now = self.now()
        row = db.execute(
            "INSERT INTO jobs (queue, kind, payload, dedupe_key, max_attempts, run_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (dedupe_key) DO NOTHING RETURNING id",
            (queue, kind, json.dumps(payload, sort_keys=True), dedupe_key, max_attempts, now + delay, now),
        ).fetchone()
        if row is not None:
            return row["id"]
        return db.execute("SELECT id FROM jobs WHERE dedupe_key = ?", (dedupe_key,)).fetchone()["id"]

    # ---- worker side
    def reserve(self, worker: str, *, queue="default", lease=30.0):
        """Atomically claim the next ready job, or return None."""
        now = self.now()
        with closing(self._connect()) as db:
            # a job whose lease expired after its last allowed attempt is given up on
            db.execute("UPDATE jobs SET state = 'dead', finished_at = ?, last_error = 'lease expired on the last attempt' "
                       "WHERE queue = ? AND state = 'running' AND lease_until <= ? AND attempts >= max_attempts",
                       (now, queue, now))
            row = db.execute(
                "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
                "WHERE id = (SELECT id FROM jobs WHERE queue = ? AND "
                "            ((state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?)) "
                "            ORDER BY run_at, id LIMIT 1) "
                "RETURNING *",
                (now + lease, worker, queue, now, now),
            ).fetchone()
            return dict(row) if row else None

    def heartbeat(self, job_id, worker, lease=30.0) -> bool:
        """Extend the lease of a long job. False means we lost it."""
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET lease_until = ? WHERE id = ? AND worker = ? AND state = 'running'",
                             (self.now() + lease, job_id, worker))
            return cur.rowcount == 1

    def complete(self, job_id, worker) -> bool:
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET state = 'done', finished_at = ?, lease_until = NULL "
                             "WHERE id = ? AND worker = ? AND state = 'running'", (self.now(), job_id, worker))
            return cur.rowcount == 1                     # False: our lease had expired and someone else owns the job

    def fail(self, job, error, *, retry_in=0.0, permanent=False) -> bool:
        """Record a failure. The job is retried later, or buried in the dead state."""
        with closing(self._connect()) as db:
            if permanent or job["attempts"] >= job["max_attempts"]:
                cur = db.execute("UPDATE jobs SET state = 'dead', last_error = ?, finished_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'", (error, self.now(), job["id"], job["worker"]))
            else:
                cur = db.execute("UPDATE jobs SET state = 'queued', last_error = ?, run_at = ?, lease_until = NULL "
                                 "WHERE id = ? AND worker = ? AND state = 'running'",
                                 (error, self.now() + retry_in, job["id"], job["worker"]))
            return cur.rowcount == 1

    # ---- operators
    def requeue_dead(self, job_id) -> bool:
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE jobs SET state = 'queued', attempts = 0, run_at = ?, finished_at = NULL "
                             "WHERE id = ? AND state = 'dead'", (self.now(), job_id))
            return cur.rowcount == 1

    def get(self, job_id):
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(row) if row else None

    def stats(self, queue="default") -> dict:
        now = self.now()
        with closing(self._connect()) as db:
            counts = {r["state"]: r["n"] for r in db.execute(
                "SELECT state, COUNT(*) AS n FROM jobs WHERE queue = ? GROUP BY state", (queue,))}
            oldest = db.execute("SELECT MIN(run_at) AS t FROM jobs WHERE queue = ? AND state = 'queued' AND run_at <= ?",
                                (queue, now)).fetchone()["t"]
        return {**{s: counts.get(s, 0) for s in ("queued", "running", "done", "dead")},
                "oldest_ready_age": round(now - oldest, 3) if oldest is not None else 0.0}
```

Read `reserve` slowly, because it is the heart of the system. One SQL statement both **finds** the next ready job and **claims** it (`UPDATE ... WHERE id = (SELECT ...) RETURNING *`). SQLite runs a statement under a write lock, so two workers can never claim the same row. On PostgreSQL the same idea is written `SELECT ... FOR UPDATE SKIP LOCKED` inside a transaction. A job is "ready" if it is `queued` and its `run_at` has come, **or** if it is `running` but its lease has expired (a crashed worker). Notice also that `complete` and `fail` check `worker = ?`: only the worker that **currently holds the lease** may finish the job.

### 9.3 It works: ordering, delays, leases, crashes

All of these tests use a fake clock, so nothing sleeps:

```python run
import os
import tempfile

from jobqueue import JobQueue

with tempfile.TemporaryDirectory() as tmp:
    clock = [1000.0]
    q = JobQueue(os.path.join(tmp, "q.db"), now=lambda: clock[0])

    first = q.enqueue("email", {"to": "ada"})
    later = q.enqueue("email", {"to": "bo"}, delay=60)
    third = q.enqueue("email", {"to": "cy"})
    order = []
    for _ in range(2):
        job = q.reserve("w1")
        order.append(job["payload"])
        q.complete(job["id"], "w1")                        # finished, so it does not come back
    print("reserve order now :", order)
    print("(bo is delayed)    next reserve ->", q.reserve("w1"))
    clock[0] += 60
    job = q.reserve("w1")
    print("after 60 s        :", job["payload"], "attempts:", job["attempts"])

    print()
    print("--- a crash and a lease ---")
    q2 = JobQueue(os.path.join(tmp, "q2.db"), now=lambda: clock[0])
    q2.enqueue("report", {"month": "2026-10"})
    mine = q2.reserve("worker-A", lease=30)
    print("A reserved it     :", mine["id"], "state:", q2.get(mine["id"])["state"], "attempts:", mine["attempts"])
    print("B right now       :", q2.reserve("worker-B"), "<- leased to A, nothing for B")
    clock[0] += 31                                         # worker A crashed or hung; the lease ran out
    taken = q2.reserve("worker-B", lease=30)
    print("B after the lease :", taken["id"], "attempts:", taken["attempts"], "worker:", taken["worker"])
    print("A wakes up, completes:", q2.complete(mine["id"], "worker-A"), "<- refused: it no longer owns the job")
    print("B completes       :", q2.complete(taken["id"], "worker-B"))
    print("final state       :", q2.get(taken["id"])["state"])
```
```text
reserve order now : ['{"to": "ada"}', '{"to": "cy"}']
(bo is delayed)    next reserve -> None
after 60 s        : {"to": "bo"} attempts: 1

--- a crash and a lease ---
A reserved it     : 1 state: running attempts: 1
B right now       : None <- leased to A, nothing for B
B after the lease : 1 attempts: 2 worker: worker-B
A wakes up, completes: False <- refused: it no longer owns the job
B completes       : True
final state       : done
```

Look at the middle: A's job is given to B after the lease expires, so **a crash does not lose the job** (at least once). But if A was not dead, only slow, then A and B **both** ran the job: this is exactly why workers must be idempotent. A's late `complete` is refused because B holds the lease now. For long jobs, the worker calls `heartbeat` to extend the lease while it is making progress, and the lease length is a trade-off: short leases recover from crashes fast but cause duplicate runs of slow jobs; long leases are safer for slow jobs but delay recovery.

### 9.4 Attempts, dedupe keys and the dead state

```python run
import os
import tempfile

from jobqueue import JobQueue

with tempfile.TemporaryDirectory() as tmp:
    clock = [0.0]
    q = JobQueue(os.path.join(tmp, "q.db"), now=lambda: clock[0])

    a = q.enqueue("invoice", {"order": 7}, dedupe_key="invoice:order-7")
    b = q.enqueue("invoice", {"order": 7}, dedupe_key="invoice:order-7")
    print("same dedupe key   :", a == b, "-> one job, ids", a, b)
    q.complete(q.reserve("w")["id"], "w")                  # finish that job so it does not get in the way

    # a job that is only allowed two attempts, and a worker that keeps crashing
    jid = q.enqueue("flaky", {}, max_attempts=2)
    for attempt in (1, 2):
        job = q.reserve("w")
        print(f"attempt {job['attempts']}: reserved; the worker dies without finishing")
        clock[0] += 31
    print("third reserve     :", q.reserve("w"))
    dead = q.get(jid)
    print("state:", dead["state"], "| attempts:", dead["attempts"], "| error:", dead["last_error"])
    print("stats:", q.stats())
    q.requeue_dead(jid)
    print("after requeue_dead:", q.get(jid)["state"], "| attempts reset to", q.get(jid)["attempts"])
```
```text
same dedupe key   : True -> one job, ids 1 1
attempt 1: reserved; the worker dies without finishing
attempt 2: reserved; the worker dies without finishing
third reserve     : None
state: dead | attempts: 2 | error: lease expired on the last attempt
stats: {'queued': 0, 'running': 0, 'done': 1, 'dead': 1, 'oldest_ready_age': 0.0}
after requeue_dead: queued | attempts reset to 0
```

A job that keeps killing its worker (a "poison" job) is eventually buried in the **dead** state instead of cycling for ever, where an operator can inspect `last_error`, fix the cause, and `requeue_dead` it.

### 9.5 Many workers, no double claims

The claim must be safe when many workers race. Here are 8 threads (each using its own database connection, like 8 worker processes) that drain 200 jobs; we record who claimed each one:

```python run
import os
import tempfile
import threading
from collections import Counter

from jobqueue import JobQueue

with tempfile.TemporaryDirectory() as tmp:
    q = JobQueue(os.path.join(tmp, "q.db"))
    for i in range(200):
        q.enqueue("task", {"n": i})

    claimed, lock = [], threading.Lock()

    def worker(name):
        while True:
            job = q.reserve(name, lease=60)
            if job is None:
                return
            with lock:
                claimed.append((job["id"], name))
            q.complete(job["id"], name)

    threads = [threading.Thread(target=worker, args=(f"w{i}",)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    per_job = Counter(job_id for job_id, _ in claimed)
    print("claims:", len(claimed), "| distinct jobs:", len(per_job), "| any job claimed twice:", any(n > 1 for n in per_job.values()))
    print("workers that did something:", len({w for _, w in claimed}) > 1)
    print("stats:", q.stats())
```
```text
claims: 200 | distinct jobs: 200 | any job claimed twice: False
workers that did something: True
stats: {'queued': 0, 'running': 0, 'done': 200, 'dead': 0, 'oldest_ready_age': 0.0}
```

200 jobs, 200 claims, no duplicates, and all done. The database's locking does what a Redis `BRPOPLPUSH` or an SQS receive does for you in those systems.

### Try it: lease length

A job normally takes 20 seconds, and sometimes 3 minutes. You set the lease to 30 seconds with no heartbeat. What happens to the slow jobs, and what are two ways to fix it?

<details><summary>Answer</summary>

After 30 seconds the lease expires while the worker is still working, so another worker takes the job and runs it too: the slow jobs run twice (or more, up to `max_attempts`, and then land in the dead state although they were only slow). Fixes: (1) have the worker call `heartbeat()` every 10 seconds while it works, so the lease follows the progress, and a crashed worker still loses it within 30 seconds; (2) set the lease above the worst expected runtime (3+ minutes), accepting a slower recovery after a crash. Making the job idempotent (section 11) is the safety net either way.

</details>

### Try it: why check the worker name?

`complete()` has `AND worker = ? AND state = 'running'`. What bug appears if you remove the worker check?

<details><summary>Answer</summary>

A worker whose lease expired (and whose job is now running on another worker) could mark it done while the new worker is still working on it, or after the new worker failed and requeued it, losing the retry. With the check, only the current lease holder can change the job, and a stale worker's `complete` returns `False`, which the worker can log as "I lost the job".

</details>

## 10. Workers

### 10.1 The worker loop

A worker is a loop: **reserve a job, run the handler, then complete or fail the job**. Everything else (retry policy, shutdown, concurrency) is detail around this loop. Our worker also classifies errors, because "what to do after a failure" depends on the failure:

```python
# worker.py
import json
import random
import signal
import threading
import time


class PermanentError(Exception):
    """This job can never succeed (bad payload, unknown kind). Do not retry; bury it."""


class RetryLater(Exception):
    """A known, temporary problem (rate limit, provider down). Retry, optionally after `delay` seconds."""

    def __init__(self, message="", delay=None):
        super().__init__(message)
        self.delay = delay


def backoff_delay(attempt: int, base=2.0, cap=300.0, rng=random.random) -> float:
    """Exponential backoff with equal jitter: half fixed, half random. attempt starts at 1."""
    delay = min(cap, base * 2 ** (attempt - 1))
    return delay / 2 + rng() * delay / 2


class Worker:
    def __init__(self, queue, handlers: dict, *, name="worker-1", queue_name="default", lease=30.0, rng=random.random):
        self.queue, self.handlers, self.name = queue, handlers, name
        self.queue_name, self.lease, self.rng = queue_name, lease, rng
        self.stopping = threading.Event()

    def run_once(self):
        """Process at most one job. Returns None (nothing to do), or 'done', 'retry', 'dead', 'lease-lost'."""
        job = self.queue.reserve(self.name, queue=self.queue_name, lease=self.lease)
        if job is None:
            return None
        handler = self.handlers.get(job["kind"])
        try:
            if handler is None:
                raise PermanentError(f"no handler for job kind {job['kind']!r}")
            handler(json.loads(job["payload"]), job)
        except PermanentError as exc:
            self.queue.fail(job, f"permanent: {exc}", permanent=True)
            return "dead"
        except RetryLater as exc:
            delay = exc.delay if exc.delay is not None else backoff_delay(job["attempts"], rng=self.rng)
            ok = self.queue.fail(job, f"retry later: {exc}", retry_in=delay)
        except Exception as exc:                                              # unexpected: assume temporary
            delay = backoff_delay(job["attempts"], rng=self.rng)
            ok = self.queue.fail(job, f"{type(exc).__name__}: {exc}", retry_in=delay)
        else:
            return "done" if self.queue.complete(job["id"], self.name) else "lease-lost"
        if not ok:
            return "lease-lost"
        return "dead" if self.queue.get(job["id"])["state"] == "dead" else "retry"

    def run_forever(self, idle_sleep=0.2):
        while not self.stopping.is_set():
            if self.run_once() is None:
                self.stopping.wait(idle_sleep)                                # nothing to do: sleep, but wake up on stop

    def stop(self):
        self.stopping.set()

    def install_signal_handlers(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: self.stop())                         # finish the current job, then exit
```

```python run
import os
import tempfile

from jobqueue import JobQueue
from worker import PermanentError, RetryLater, Worker

attempts_seen = {"flaky": 0}


def send_email(payload, job):
    if "@" not in payload["to"]:
        raise PermanentError(f"bad address {payload['to']!r}")


def flaky(payload, job):
    attempts_seen["flaky"] += 1
    if attempts_seen["flaky"] < 3:
        raise ConnectionError("provider timed out")


def busy(payload, job):
    raise RetryLater("rate limited", delay=45)


with tempfile.TemporaryDirectory() as tmp:
    clock = [0.0]
    q = JobQueue(os.path.join(tmp, "q.db"), now=lambda: clock[0])
    w = Worker(q, {"email": send_email, "flaky": flaky, "busy": busy}, rng=lambda: 0.5)

    ids = {k: q.enqueue(k, {"to": "ada@example.com"}) for k in ("email", "flaky", "busy")}
    ids["bad"] = q.enqueue("email", {"to": "not-an-address"})
    ids["unknown"] = q.enqueue("mystery", {})

    results = []
    while (outcome := w.run_once()) is not None:
        results.append(outcome)
    print("first pass outcomes:", results)
    for name, jid in ids.items():
        j = q.get(jid)
        print(f"  {name:8} state={j['state']:7} attempts={j['attempts']} run_at={j['run_at']:>5} error={j['last_error']}")

    for round_number in range(1, 7):                      # time passes; the delayed retries become ready
        clock[0] += 400
        outcomes = []
        while (outcome := w.run_once()) is not None:
            outcomes.append(outcome)
        print(f"round {round_number} outcomes:", outcomes)
    print("final states:")
    for name, jid in ids.items():
        j = q.get(jid)
        print(f"  {name:8} state={j['state']:5} attempts={j['attempts']}")
```
```text
first pass outcomes: ['done', 'retry', 'retry', 'dead', 'dead']
  email    state=done    attempts=1 run_at=  0.0 error=None
  flaky    state=queued  attempts=1 run_at=  1.5 error=ConnectionError: provider timed out
  busy     state=queued  attempts=1 run_at= 45.0 error=retry later: rate limited
  bad      state=dead    attempts=1 run_at=  0.0 error=permanent: bad address 'not-an-address'
  unknown  state=dead    attempts=1 run_at=  0.0 error=permanent: no handler for job kind 'mystery'
round 1 outcomes: ['retry', 'retry']
round 2 outcomes: ['done', 'retry']
round 3 outcomes: ['retry']
round 4 outcomes: ['dead']
round 5 outcomes: []
round 6 outcomes: []
final states:
  email    state=done  attempts=1
  flaky    state=done  attempts=3
  busy     state=dead  attempts=5
  bad      state=dead  attempts=1
  unknown  state=dead  attempts=1
```

### 10.2 Details of a good worker

- **Graceful shutdown.** Deployments send `SIGTERM`. A worker that is killed mid-job leaves work half done. A good worker stops *taking* jobs, **finishes** the current one, then exits (`install_signal_handlers` above). Give the orchestrator a grace period longer than your longest job, or rely on leases and idempotency for the rest.
- **Concurrency model.** One job at a time per process is simplest and safest. Scale by running more worker **processes**; use **threads** for I/O-bound jobs and **async** workers (arq) for many concurrent network calls; CPU-heavy jobs need processes (core.21).
- **Time limits.** A job that hangs holds a worker slot for ever. Set a **hard time limit** (kill or abandon after N seconds) and let the lease expire so another worker can retry.
- **Small payloads, pass ids.** Put `{"order_id": 7}` in the payload, not the whole order. The data may have changed by the time the job runs, and the worker should read the *current* truth. Big blobs belong in file or object storage, referenced by key.
- **Serialisation.** JSON only. (Celery's old default, pickle, executes code from whoever can write to the broker, swe.07 section 14.7.)
- **Version your payloads.** Jobs can sit in the queue across a deploy. A new worker must still understand old jobs (or old ones must be drained first), so add fields instead of renaming them, and include a `v` field if the format must change.
- **Separate queues by workload.** Put slow reports and fast e-mails on different queues with different workers, so a flood of reports cannot delay password-reset e-mails.
- **Prefetching.** Some brokers hand a worker several jobs in advance for speed. A worker that reserves 100 jobs and then crashes delays all of them; for long jobs prefetch **one**.
- **Never trust the payload.** Jobs come from your own code, but validate them anyway (Pydantic), and treat an invalid payload as a **permanent** error.
- **Log with the job id** and the **request id** that created it, so you can follow one user action across the web app and the worker (section 15).

### 10.3 Result and status

A queue is "fire and forget" by default. When the caller needs an outcome, store it **in your own tables** (a `reports` table with `status`, `file_path`, `error`) rather than relying on a broker's result store, which expires and is not queryable. The job id plus a status endpoint (section 8.2) is the usual pattern, and your database remains the truth.

### Try it: classify the error

For each, choose PermanentError, RetryLater, or a generic retry: (a) the payload says `{"order_id": "abc"}`; (b) the e-mail provider returns HTTP 503; (c) the provider returns HTTP 429 with `Retry-After: 60`; (d) the database is restarting; (e) the recipient address was rejected as non-existent.

<details><summary>Answer</summary>

(a) **Permanent**: the payload can never become valid; retrying wastes capacity. (b) **Generic retry** with backoff: temporary. (c) **RetryLater(delay=60)**: honour the provider's instruction. (d) **Generic retry**: transient, it will pass. (e) **Permanent**: a hard bounce; retrying harms your sender reputation. (A 4xx from a provider is usually permanent except 408, 425 and 429; 5xx is usually transient.)

</details>

### Try it: why not hold the whole object?

A teammate puts the complete `Order` (customer, lines, prices) in the job payload "to save a database query in the worker". Give two problems.

<details><summary>Answer</summary>

(1) **Stale data**: the order may be cancelled or edited before the job runs, and the worker would act on the old copy (e-mail a receipt for a cancelled order). (2) **Size and privacy**: personal data sits in the broker, in logs and in the dead-letter queue, and large messages slow the broker. Pass the order id and let the worker read the current state. (The exception is an event that deliberately records "what happened", such as an audit entry.)

</details>


## 11. Idempotent workers: the same result when a task runs twice

This section delivers the first outcome of the chapter: **design a worker that gives the same result when a task runs twice, and prove it.**

### 11.1 Duplicates are normal, not rare

With at-least-once delivery, a job runs twice whenever the system is unsure whether it finished. That happens often:

- The worker **crashed or was killed** after doing the work but before the ack (a deploy, an out-of-memory kill, a power cut).
- The **lease expired** while a slow worker was still working (section 9.3), so a second worker took over.
- The worker finished, but the **ack was lost** (network error to the broker).
- The **producer retried** the enqueue because it did not see the first reply (the web request timed out), creating two jobs.
- An operator **re-queued** a dead job, or a bug replayed a batch.
- A message broker redelivered after a **failover**.

You cannot prevent these, so you design for them. The goal is not "a job never runs twice"; it is **"running it twice is the same as running it once."** That property is called **idempotency** (you met it for HTTP in swe.07 section 13).

### 11.2 The crash windows

Follow one job through a worker. Each arrow is a place where the process can die. After a death, the broker only knows whether the ack happened, so the job comes back and runs **from the beginning**:

```text
 reserve --> (check) --> EFFECT --> (record) --> ack
    ^           ^           ^          ^           ^
    |           |           |          |           `-- dies here: everything is done, the job is redelivered
    |           |           |          `-- dies here: effect done, but our own record does not say so
    |           |           `-- dies in the middle of the effect: half done
    |           `-- dies before the effect: nothing happened (the easy case)
    `-- the job is leased
```

A design is idempotent if the final outcome is the same **for a crash at each of those points**. The way to be sure is to test exactly that, which is what we do below.

### 11.3 Five tools

| # | Tool | Idea | Example |
|---|---|---|---|
| 1 | **Natural idempotency** | choose operations that are safe to repeat | `UPDATE users SET plan='pro' WHERE id=7` (not `credits = credits + 10`); `INSERT ... ON CONFLICT DO NOTHING`; `PUT`; overwrite a file |
| 2 | **Conditional transition** | only move forward from the expected state | `UPDATE invoices SET status='sent' WHERE id=7 AND status='draft'`, and check the row count |
| 3 | **Dedupe record in the same transaction** | the effect and the "I did it" marker commit together | for effects inside your own database |
| 4 | **Idempotency key to the outside world** | pass a stable key to the e-mail, payment or API provider, which refuses to repeat | `Idempotency-Key: welcome:7` |
| 5 | **Outbox** | create the *job* in the same transaction as the business change | an order and its "send receipt" job commit or fail together |

Tool 3 is easy because one database transaction is atomic. The difficult case is an **effect in the outside world**: you cannot put an e-mail into your database transaction. For those you need tool 4 (the provider remembers the key) or you must accept either "maybe lost" or "maybe duplicated" and choose consciously. Let us build both and test them.

### 11.4 The e-mail worker, first the wrong way

We need a fake e-mail provider. Like real ones, it can **honour an idempotency key** (it recognises a repeat and returns the original message id), and it can simulate the nastiest failure: it **sends the message but the response is lost**, so the caller sees a timeout:

```python
# mailer.py
import sqlite3
from contextlib import closing


class ProviderTimeout(Exception):
    pass


class FakeMailProvider:
    """Stands in for an e-mail API. `outbox` is what recipients really received."""

    def __init__(self, honours_idempotency_keys=True):
        self.honours_keys = honours_idempotency_keys
        self.outbox, self._by_key = [], {}
        self.lose_next_response = False

    def send(self, to, subject, body, idempotency_key=None):
        if self.honours_keys and idempotency_key is not None and idempotency_key in self._by_key:
            return self._by_key[idempotency_key]                    # a repeat: do not send again
        message_id = f"msg-{len(self.outbox) + 1}"
        self.outbox.append({"id": message_id, "to": to, "subject": subject})
        if idempotency_key is not None:
            self._by_key[idempotency_key] = message_id
        if self.lose_next_response:
            self.lose_next_response = False
            raise ProviderTimeout("sent, but the response never arrived")
        return message_id


class Crash(BaseException):
    """Simulates the PROCESS DYING. It derives from BaseException so the worker's `except Exception` cannot catch it."""


class CrashAt:
    def __init__(self, point=None):
        self.point = point

    def hit(self, name):
        if name == self.point:
            self.point = None                                     # crash once
            raise Crash(name)


def init_email_log(path):
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT)")


def make_naive_handler(provider, crash):
    def handler(payload, job):
        crash.hit("before-send")
        provider.send(payload["to"], "Welcome!", "Hello and welcome.")          # no key, no record
        crash.hit("after-send")
    return handler


def make_safe_handler(db_path, provider, crash):
    def handler(payload, job):
        key = f"welcome:{payload['user_id']}"                  # a BUSINESS key: it names the thing done, not the job
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            crash.hit("start")
            row = db.execute("SELECT state FROM email_log WHERE key = ?", (key,)).fetchone()
            if row and row[0] == "sent":
                return                                          # a duplicate delivery: already done
            db.execute("INSERT OR IGNORE INTO email_log (key, to_addr, state) VALUES (?, ?, 'sending')", (key, payload["to"]))
            crash.hit("after-claim")
            message_id = provider.send(payload["to"], "Welcome!", "Hello and welcome.", idempotency_key=key)   # safe to repeat
            crash.hit("after-send")
            db.execute("UPDATE email_log SET state = 'sent', provider_id = ? WHERE key = ?", (message_id, key))
            crash.hit("after-record")
    return handler
```

Now a test harness that runs one job, **kills the worker at a chosen point**, lets the lease expire, starts a second worker, and counts the e-mails that really went out:

```python
# crashtest.py
import os
import tempfile

from jobqueue import JobQueue
from mailer import Crash, CrashAt, FakeMailProvider, init_email_log
from worker import Worker


def run_job_with_crash(make_handler, crash_point, *, duplicate_jobs=1, lose_response=False, honours_keys=True):
    """Return (e-mails received, final job states)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "q.db")
        clock = [0.0]
        q = JobQueue(path, now=lambda: clock[0])
        init_email_log(path)
        provider = FakeMailProvider(honours_idempotency_keys=honours_keys)
        provider.lose_next_response = lose_response
        crash = CrashAt(crash_point)
        for _ in range(duplicate_jobs):
            q.enqueue("welcome", {"user_id": 7, "to": "ada@example.com"})

        first = Worker(q, {"welcome": make_handler(path, provider, crash)}, name="worker-1", lease=30)
        try:
            first.run_once()
        except Crash:
            pass                                                # the process is dead: no complete(), no fail()

        for _ in range(8):                                      # time passes; the lease expires; a new worker starts
            clock[0] += 31
            second = Worker(q, {"welcome": make_handler(path, provider, CrashAt(None))}, name="worker-2", lease=30, rng=lambda: 0.0)
            while second.run_once() is not None:
                pass
        states = [q.get(i)["state"] for i in range(1, duplicate_jobs + 1)]
        return len(provider.outbox), states
```

First, the **naive** handler (no key, no record). Kill it before the send, and after the send:

```python run
import mailer
from crashtest import run_job_with_crash

naive = lambda path, provider, crash: mailer.make_naive_handler(provider, crash)

print(f"{'scenario':40} e-mails received   job")
for label, point, extra in [
    ("no crash", None, {}),
    ("crash BEFORE the send", "before-send", {}),
    ("crash AFTER the send, before the ack", "after-send", {}),
    ("provider loses the response once", None, {"lose_response": True}),
    ("the same job was enqueued twice", None, {"duplicate_jobs": 2}),
]:
    emails, states = run_job_with_crash(naive, point, **extra)
    verdict = "OK" if emails == 1 else "DUPLICATE" if emails > 1 else "LOST"
    print(f"{label:40} {emails}  {verdict:10} {states}")
```
```text
scenario                                 e-mails received   job
no crash                                 1  OK         ['done']
crash BEFORE the send                    1  OK         ['done']
crash AFTER the send, before the ack     2  DUPLICATE  ['done']
provider loses the response once         2  DUPLICATE  ['done']
the same job was enqueued twice          2  DUPLICATE  ['done', 'done']
```

Three scenarios send **two e-mails**. This is what "at least once" looks like without defences. (Nothing was lost, which is the good half of the bargain.)

### 11.5 The e-mail worker, the right way

The safe handler (shown above) does four things, each aimed at a crash window:

1. It takes a **business key** (`welcome:7`) for what is being done: "the welcome e-mail for user 7". The job id would be the wrong choice, because two *different* jobs asking for the same e-mail (the double-enqueue case) must still produce one e-mail.
2. It checks the **record**: if the log says `sent`, it returns at once (duplicate delivery after a crash *after* the record).
3. It records **intent** (`sending`) before the effect, and
4. It passes the key to the provider as the **idempotency key**, so even if the process died after sending but before recording (or the response was lost), the retry sends the *same* key and the provider refuses to send a second message.

Now run the same matrix, plus one crash at every point inside the handler:

```python run
import mailer
from crashtest import run_job_with_crash

safe = lambda path, provider, crash: mailer.make_safe_handler(path, provider, crash)

print(f"{'scenario':44} e-mails received   job")
scenarios = [
    ("no crash", None, {}),
    ("crash at start", "start", {}),
    ("crash after the claim, before the send", "after-claim", {}),
    ("crash after the send, before the record", "after-send", {}),
    ("crash after the record, before the ack", "after-record", {}),
    ("provider loses the response once", None, {"lose_response": True}),
    ("the same job was enqueued twice", None, {"duplicate_jobs": 2}),
    ("enqueued twice AND a crash after the send", "after-send", {"duplicate_jobs": 2}),
]
all_good = True
for label, point, extra in scenarios:
    emails, states = run_job_with_crash(safe, point, **extra)
    all_good &= emails == 1 and set(states) == {"done"}
    print(f"{label:44} {emails}  {'OK' if emails == 1 else 'WRONG':10} {states}")
print("every scenario: exactly one e-mail and every job finished:", all_good)
```
```text
scenario                                     e-mails received   job
no crash                                     1  OK         ['done']
crash at start                               1  OK         ['done']
crash after the claim, before the send       1  OK         ['done']
crash after the send, before the record      1  OK         ['done']
crash after the record, before the ack       1  OK         ['done']
provider loses the response once             1  OK         ['done']
the same job was enqueued twice              1  OK         ['done', 'done']
enqueued twice AND a crash after the send    1  OK         ['done', 'done']
every scenario: exactly one e-mail and every job finished: True
```

One e-mail in every scenario, and every job ends `done`. This is the property to aim for, and a test like this one (a crash at each point, then a second worker) is how you prove it, instead of hoping.

#### The honest limit: when the provider has no idempotency key

What if the provider **cannot** deduplicate? Then the crash window between "send" and "record" cannot be closed. You must choose, knowingly:

```python run
import mailer
from crashtest import run_job_with_crash

safe = lambda path, provider, crash: mailer.make_safe_handler(path, provider, crash)

emails, _ = run_job_with_crash(safe, "after-send", honours_keys=False)
print("provider ignores keys, crash after the send:", emails, "e-mails  <- a duplicate is possible")
```
```text
provider ignores keys, crash after the send: 2 e-mails  <- a duplicate is possible
```

| Choice | What you do | Failure | Fits |
|---|---|---|---|
| **At least once** | send, then record; retry on doubt | a rare duplicate | notifications where a duplicate is harmless |
| **At most once** | record `sent` first, then send; never retry in doubt | a rare lost message | when a duplicate is worse than a loss |
| **Reconcile** | record intent, send, and later ask the provider "did you send message X?" (many have a lookup API) | extra code | payments, money |

For payments there is almost always an idempotency key or a lookup API, and you should insist on one. Where neither exists, reduce the harm instead: a duplicate "your report is ready" e-mail is annoying, a duplicate charge is a disaster, so the design should reflect the cost.

### 11.6 Database-only effects: one transaction

When the effect lives in **your own database**, idempotency is easy, because the effect and the marker can commit together. "Credit the customer's loyalty points for order 7" must not run twice:

```python run
import sqlite3

db = sqlite3.connect(":memory:", isolation_level=None)
db.executescript("""
    CREATE TABLE points (user_id INTEGER PRIMARY KEY, balance INTEGER NOT NULL);
    CREATE TABLE points_awarded (order_id INTEGER PRIMARY KEY);          -- the dedupe record
    INSERT INTO points VALUES (1, 0);
""")


def award_points_wrong(order_id, user_id, n):
    db.execute("UPDATE points SET balance = balance + ? WHERE user_id = ?", (n, user_id))       # relative update, no marker


def award_points(order_id, user_id, n, crash_after_effect=False):
    db.execute("BEGIN IMMEDIATE")
    try:
        done = db.execute("INSERT OR IGNORE INTO points_awarded VALUES (?)", (order_id,)).rowcount     # 1 = first time
        if done:
            db.execute("UPDATE points SET balance = balance + ? WHERE user_id = ?", (n, user_id))
        if crash_after_effect:
            raise RuntimeError("process died before COMMIT")
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")                                           # marker and effect disappear TOGETHER
        raise


def balance():
    return db.execute("SELECT balance FROM points WHERE user_id = 1").fetchone()[0]


award_points_wrong(7, 1, 50)
award_points_wrong(7, 1, 50)
print("wrong, run twice          :", balance())
db.execute("UPDATE points SET balance = 0")

try:
    award_points(7, 1, 50, crash_after_effect=True)
except RuntimeError:
    pass
print("crash before commit       :", balance(), "(nothing happened)")
award_points(7, 1, 50)
award_points(7, 1, 50)
award_points(7, 1, 50)
print("then run three times      :", balance(), "(exactly one award)")
```
```text
wrong, run twice          : 100
crash before commit       : 0 (nothing happened)
then run three times      : 50 (exactly one award)
```

The marker (`points_awarded.order_id` with a primary key) and the effect succeed or fail **together**, so there is no window in which one is true and the other is not. The same pattern, "claim with a unique key in the same transaction", protects order creation, stock changes and anything else that stays inside the database.

### 11.7 The outbox: enqueue in the same transaction as the business change

There is a crash window *before* the worker even exists: the web request saves an order, then enqueues "send receipt". If the process dies between the two, the order exists and the receipt job never will. Reversing the order (enqueue first) can produce a receipt for an order that was never saved. The **outbox pattern** removes the window: write the business row **and** the job row in **one transaction**. A database-backed queue makes this natural (`enqueue_in` takes the caller's connection):

```python run
import os
import sqlite3
import tempfile
from contextlib import closing

from jobqueue import JobQueue
from mailer import Crash, CrashAt

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "shop.db")
    q = JobQueue(path)
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, total_cents INTEGER)")

    def place_order_two_steps(total, crash):
        with closing(sqlite3.connect(path, isolation_level=None)) as db:
            order_id = db.execute("INSERT INTO orders (total_cents) VALUES (?)", (total,)).lastrowid     # committed
        crash.hit("between")
        q.enqueue("receipt", {"order_id": order_id})

    def place_order_outbox(total, crash):
        with closing(sqlite3.connect(path, isolation_level=None)) as db:
            q_db = q._connect()
            try:
                q_db.execute("BEGIN IMMEDIATE")
                order_id = q_db.execute("INSERT INTO orders (total_cents) VALUES (?)", (total,)).lastrowid
                crash.hit("between")
                q.enqueue_in(q_db, "receipt", {"order_id": order_id})
                q_db.execute("COMMIT")
            except BaseException:
                q_db.execute("ROLLBACK")
                raise
            finally:
                q_db.close()

    def counts():
        with closing(sqlite3.connect(path, isolation_level=None)) as db:
            return db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

    try:
        place_order_two_steps(100, CrashAt("between"))
    except Crash:
        pass
    print("two steps, crash in between : (orders, receipt jobs) =", counts(), "<- an order with no receipt, for ever")

    try:
        place_order_outbox(200, CrashAt("between"))
    except Crash:
        pass
    print("outbox, crash in between    : (orders, receipt jobs) =", counts(), "<- unchanged: the second order was rolled back whole")
    place_order_outbox(300, CrashAt(None))
    print("outbox, no crash            : (orders, receipt jobs) =", counts())
```
```text
two steps, crash in between : (orders, receipt jobs) = (1, 0) <- an order with no receipt, for ever
outbox, crash in between    : (orders, receipt jobs) = (1, 0) <- unchanged: the second order was rolled back whole
outbox, no crash            : (orders, receipt jobs) = (2, 1)
```

With Redis or RabbitMQ the broker is a *different* system from your database, so a single transaction cannot span both. Then you write the job into an **outbox table** in your database, and a small relay process copies outbox rows to the broker, marking them sent (at-least-once, so the consumer is idempotent). That is the same pattern with one more hop.

### 11.8 The report worker: deterministic and atomic

A report job has two awkward properties: the result is a **file**, and a crash can leave a **half-written** file that a reader might open. Two rules make it idempotent:

1. **Deterministic output.** The same inputs must give the same bytes. Sort rows, do not embed "now" or random ids (take the timestamp from the job's payload), and a rerun overwrites the file with identical content.
2. **Atomic publish.** Write to a temporary file in the same folder, flush it to disk, then `os.replace` it onto the final name. Readers see either the old complete file or the new complete file, never half of one.

```python
# reports.py
import csv
import hashlib
import io
import os


def build_report(rows, month: str) -> bytes:
    """Deterministic: sorted rows, a fixed header, no clock, no randomness."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["month", "order_id", "customer", "total_cents"])
    for order_id, customer, total in sorted(rows):
        writer.writerow([month, order_id, customer, total])
    return out.getvalue().encode()


def write_naive(path, data: bytes, crash=None):
    with open(path, "wb") as f:                      # visible (and truncated) as soon as it is opened
        f.write(data[: len(data) // 2])
        if crash:
            crash.hit("mid-write")
        f.write(data[len(data) // 2:])


def write_atomic(path, data: bytes, crash=None):
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        f.write(data[: len(data) // 2])
        if crash:
            crash.hit("mid-write")
        f.write(data[len(data) // 2:])
        f.flush()
        os.fsync(f.fileno())                          # the bytes are on disk before the rename
    if crash:
        crash.hit("before-replace")
    os.replace(tmp, path)                             # atomic on the same filesystem


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
```

```python run
import os
import tempfile

from mailer import Crash, CrashAt
from reports import build_report, digest, write_atomic, write_naive

rows = [(3, "cy", 990), (1, "ada", 2500), (2, "bo", 4200)]
shuffled = [rows[2], rows[0], rows[1]]
print("same rows in any order -> same bytes:", build_report(rows, "2026-10") == build_report(shuffled, "2026-10"))
data = build_report(rows, "2026-10")

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "report-2026-10.csv")

    try:
        write_naive(path, data, CrashAt("mid-write"))
    except Crash:
        pass
    print("naive, crash mid-write  : file exists, size", os.path.getsize(path), "of", len(data), "<- a reader sees half a report")
    os.remove(path)

    for point in ("mid-write", "before-replace"):
        try:
            write_atomic(path, data, CrashAt(point))
        except Crash:
            pass
        print(f"atomic, crash {point:14}: final file exists:", os.path.exists(path), "| leftovers:", [f for f in os.listdir(tmp) if f.endswith(".tmp")] != [])
        for leftover in [f for f in os.listdir(tmp) if f.endswith(".tmp")]:
            os.remove(os.path.join(tmp, leftover))

    write_atomic(path, data)                          # the retry
    first = digest(path)
    write_atomic(path, data)                          # a duplicate run
    print("run twice               : same digest:", digest(path) == first, "| size", os.path.getsize(path))
```
```text
same rows in any order -> same bytes: True
naive, crash mid-write  : file exists, size 45 of 90 <- a reader sees half a report
atomic, crash mid-write     : final file exists: False | leftovers: True
atomic, crash before-replace: final file exists: False | leftovers: True
run twice               : same digest: True | size 90
```

The retry after a crash simply redoes everything, and a duplicate run overwrites the file with identical bytes. If the report is expensive, the handler can first check "does the final file already exist with the expected digest?" and skip. Clean up stale `.tmp` files in a housekeeping job.

### 11.9 A checklist for task design

| Smell in a task | Why it breaks on a repeat | Safer form |
|---|---|---|
| `balance += 10`, `counter += 1` | repeats add again | set an absolute value, or record a dedupe key with the change |
| `INSERT` a row | repeats create duplicates | `UNIQUE` business key plus `ON CONFLICT DO NOTHING` / upsert |
| send e-mail / SMS / push | repeats message the user again | provider idempotency key; or log of sent keys |
| charge / refund | repeats move money twice | idempotency key to the payment provider; unique `(order_id, kind)` |
| append to a file or list | repeats duplicate lines | write whole files atomically; keyed upserts |
| `uuid4()`, `now()`, `random()` inside the handler | repeats produce different values | take them from the payload; derive ids from the job |
| "create a thing and return its id" | a second thing is created | pass the id in (made by the producer) |
| multi-step work where step 2 failed | step 1 is redone | each step idempotent, or track progress per step |
| call another service, then update our DB | a crash in between leaves a mismatch | idempotency key + state machine (`pending`, `sending`, `sent`) |

### Try it: which window?

A handler does: (1) read the order, (2) call the payment API (no idempotency key support), (3) save `paid = true` in the database, then returns. The process is killed between steps 2 and 3. What happens on the retry, and what can you change?

<details><summary>Answer</summary>

The retry starts at step 1, sees `paid = false`, and calls the payment API again: the customer is charged twice. Changes, best first: (a) use an API that accepts an **idempotency key** and pass `order-7-payment`; (b) if the API has a **lookup**, query "is there a charge for reference order-7?" before charging; (c) record intent (`charging`) before the call and treat a retry in that state as "unknown, reconcile with the provider" instead of charging blindly. If none of these is possible, change the process so a human or a later reconciliation job resolves the doubtful cases.

</details>

### Try it: key choice

For a "monthly invoice e-mail", which key makes the e-mail idempotent: the job id, `invoice:{customer_id}:{year}-{month}`, or the current time?

<details><summary>Answer</summary>

`invoice:{customer_id}:{year}-{month}`. It names the real-world thing ("the invoice e-mail for this customer and this month"), so two jobs created by a double-click, a re-run of the scheduler or an operator all map to one e-mail. The job id differs for every job (no protection against duplicate jobs), and the current time differs on every attempt (no protection at all).

</details>

## 12. Retries, backoff and dead letters

### 12.1 A retry policy

Retries turn temporary failures into successes, but a careless policy makes outages worse. Decide five things:

1. **Which errors are retried** (section 10.2): transient ones only. Permanent errors go to the dead state at once.
2. **How many attempts** (`max_attempts`), or a **deadline** ("give up after 24 hours").
3. **How long to wait between attempts**: exponential backoff, so a struggling dependency gets room to recover.
4. **Jitter**: randomness, so thousands of jobs that failed together do not all retry in the same second.
5. **A cap** on the delay, so attempt 12 does not wait 3 days.

The worker used **equal jitter**: half of the delay is fixed and half random. With `base = 2` seconds and a cap of 300 seconds, the delay range for each attempt is:

```python run
from worker import backoff_delay

print(f"{'attempt':>7} {'lowest':>8} {'highest':>8}   (seconds)")
for attempt in range(1, 10):
    low, high = backoff_delay(attempt, rng=lambda: 0.0), backoff_delay(attempt, rng=lambda: 1.0)
    print(f"{attempt:>7} {low:>8.1f} {high:>8.1f}")
total_high = sum(backoff_delay(a, rng=lambda: 1.0) for a in range(1, 5))        # 5 attempts have 4 waits between them
print(f"five attempts (four waits) are over after at most {total_high:.0f} seconds")
```
```text
attempt   lowest  highest   (seconds)
      1      1.0      2.0
      2      2.0      4.0
      3      4.0      8.0
      4      8.0     16.0
      5     16.0     32.0
      6     32.0     64.0
      7     64.0    128.0
      8    128.0    256.0
      9    150.0    300.0
five attempts (four waits) are over after at most 30 seconds
```

For a provider outage that may last an hour, five attempts over half a minute is far too short; the policy must match the failure you expect. A common choice for e-mail and webhooks is a long tail, such as retrying for up to a day or two, which needs a higher cap and `max_attempts` of 10 to 20.

### 12.2 Retry storms and the circuit breaker

When a dependency is down, **every** job calls it, fails, waits, and calls it again. The retries pile load on a system that is already struggling and fill your workers with doomed work. A **circuit breaker** notices repeated failures and stops calling for a while:

- **Closed**: calls go through; failures are counted.
- **Open**: after N failures, calls are refused immediately (the job is rescheduled without touching the provider) for a cool-down.
- **Half-open**: after the cool-down, let one trial call through; success closes the circuit, failure opens it again.

```python run
class CircuitBreaker:
    def __init__(self, failure_threshold=3, cool_down=30.0, now=None):
        self.threshold, self.cool_down, self.now = failure_threshold, cool_down, now
        self.failures, self.opened_at = 0, None

    @property
    def state(self):
        if self.opened_at is None:
            return "closed"
        return "half-open" if self.now() - self.opened_at >= self.cool_down else "open"

    def allow(self):
        return self.state != "open"

    def record(self, ok):
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.threshold or self.state == "half-open":
                self.opened_at = self.now()


clock = [0.0]
breaker = CircuitBreaker(now=lambda: clock[0])
provider_up = False
calls_made = 0
log = []
for second in range(0, 100, 5):
    clock[0] = second
    if not breaker.allow():
        log.append((second, "skipped (open)"))
        continue
    calls_made += 1
    ok = provider_up or second >= 60                      # the provider recovers at t = 60
    breaker.record(ok)
    log.append((second, f"called -> {'ok' if ok else 'FAILED'} [{breaker.state}]"))
for second, what in log:
    print(f"t={second:>3}s  {what}")
print("calls actually made to the provider:", calls_made, "of", len(log), "attempts")
```
```text
t=  0s  called -> FAILED [closed]
t=  5s  called -> FAILED [closed]
t= 10s  called -> FAILED [open]
t= 15s  skipped (open)
t= 20s  skipped (open)
t= 25s  skipped (open)
t= 30s  skipped (open)
t= 35s  skipped (open)
t= 40s  called -> FAILED [open]
t= 45s  skipped (open)
t= 50s  skipped (open)
t= 55s  skipped (open)
t= 60s  skipped (open)
t= 65s  skipped (open)
t= 70s  called -> ok [closed]
t= 75s  called -> ok [closed]
t= 80s  called -> ok [closed]
t= 85s  called -> ok [closed]
t= 90s  called -> ok [closed]
t= 95s  called -> ok [closed]
calls actually made to the provider: 10 of 20 attempts
```

While the provider was down (until t = 60 s) the breaker let through 4 calls instead of 12, and it probed the provider again each time the cool-down passed (the failed probe at t = 40 s opened the circuit again; the one at t = 70 s succeeded). In a worker, an open circuit raises `RetryLater(delay=cool_down)` so the job waits without burning an attempt on a call that cannot work. (A rescheduled job still counts an attempt in our queue since attempts are counted at reservation; in a real system give such "deferred, not tried" outcomes their own handling, or a larger `max_attempts`.)

### 12.3 Dead letters

A job in the dead state is not garbage; it is a **work item that needs a human or a fix**. Treat the dead-letter queue as an inbox:

1. **Alert** when it is non-empty, or growing. A silent DLQ means silent data loss.
2. **Inspect**: the stored `last_error`, the payload, the attempt count, the timeline. Keep enough context to understand the failure, but do not store secrets in payloads or errors.
3. **Fix the cause**: a code bug, a bad payload, a configuration problem, a provider account limit.
4. **Redrive**: `requeue_dead` puts the job back with a clean attempt counter. This is safe only because the handler is idempotent (a job in the dead state may have partly run).
5. **Learn**: each class of failure should lead to a better validation, a clearer permanent-versus-transient decision, or a missing alert.

```python run
import os
import tempfile
from contextlib import closing

from jobqueue import JobQueue
from worker import PermanentError, Worker

CONFIG = {"template": None}                              # a deploy forgot to set the template


def send_newsletter(payload, job):
    if CONFIG["template"] is None:
        raise PermanentError("template not configured")


with tempfile.TemporaryDirectory() as tmp:
    clock = [0.0]
    q = JobQueue(os.path.join(tmp, "q.db"), now=lambda: clock[0])
    w = Worker(q, {"newsletter": send_newsletter})
    for n in range(3):
        q.enqueue("newsletter", {"issue": n})
    while w.run_once():
        pass
    print("stats after the first pass:", q.stats())

    with closing(q._connect()) as db:
        dead = [dict(r) for r in db.execute("SELECT id, kind, attempts, last_error FROM jobs WHERE state = 'dead'")]
    print("the dead-letter inbox:")
    for row in dead:
        print("  ", row)

    CONFIG["template"] = "weekly.html"                   # the operator fixes the configuration...
    for row in dead:
        q.requeue_dead(row["id"])                        # ...and redrives the jobs
    while w.run_once():
        pass
    print("stats after the redrive   :", q.stats())
```
```text
stats after the first pass: {'queued': 0, 'running': 0, 'done': 0, 'dead': 3, 'oldest_ready_age': 0.0}
the dead-letter inbox:
   {'id': 1, 'kind': 'newsletter', 'attempts': 1, 'last_error': 'permanent: template not configured'}
   {'id': 2, 'kind': 'newsletter', 'attempts': 1, 'last_error': 'permanent: template not configured'}
   {'id': 3, 'kind': 'newsletter', 'attempts': 1, 'last_error': 'permanent: template not configured'}
stats after the redrive   : {'queued': 0, 'running': 0, 'done': 3, 'dead': 0, 'oldest_ready_age': 0.0}
```

### 12.4 Crash loops and timeouts

- A job that **crashes the worker** (out of memory, segmentation fault) never reaches `fail()`. Because our queue counts an attempt when it is **reserved**, not when it fails, such a job still uses up its attempts and ends in the dead state (section 9.4) instead of crashing workers for ever.
- A job that **hangs** holds a worker slot. Use a hard **time limit** per job (processes can be killed; threads cannot), and a lease shorter than the limit plus a heartbeat so that a stuck worker loses the job.
- Alert on **queue age**, not only on errors (section 15): a worker pool that is stuck produces no errors at all.

### Try it: size the policy

An e-mail provider has outages of up to 30 minutes about once a month. You set `max_attempts = 5`, base 2 s, cap 300 s. What happens to the e-mails queued during an outage, and what would you change?

<details><summary>Answer</summary>

Five attempts with those delays are over after at most about 30 seconds (waits of at most 2, 4, 8 and 16 s), so every e-mail in the outage window ends in the dead-letter state: hundreds of dead jobs to redrive by hand. Change the policy to match the failure: for example `max_attempts = 12` with `base = 30` and `cap = 900`, which keeps retrying for several hours, plus a circuit breaker so the retries do not hammer the provider, plus an alert if the DLQ still grows.

</details>

### Try it: redrive safely?

Is it safe to redrive every job in the dead state with one command? What must be true?

<details><summary>Answer</summary>

Only if the handlers are idempotent (a dead job may have partly run before failing), the cause has really been fixed (otherwise they all die again), and the load is acceptable (redrive a few first, or rate-limit the redrive, because 10,000 jobs arriving at once may overwhelm the dependency that caused the trouble). Review the dead jobs for ones that should be *discarded* (obsolete, for deleted users) rather than retried.

</details>

## 13. Task-queue libraries: Celery, RQ and arq

You built the pieces; now you can read the documentation of the real tools and know what each knob does. None of these is installed here, so this section shows **code to read and to run on your own machine**, not captured output.

### 13.1 How the concepts map

| Concept (our queue) | Celery | RQ | arq |
|---|---|---|---|
| broker | Redis, RabbitMQ, SQS | Redis | Redis |
| enqueue | `task.delay(args)`, `task.apply_async(countdown=60)` | `queue.enqueue(func, args)` | `await redis.enqueue_job("name", args, _defer_by=60)` |
| worker | `celery -A app worker` | `rq worker` | `arq module.WorkerSettings` |
| handler | `@app.task` function | any importable function | `async def f(ctx, ...)` |
| retries | `autoretry_for`, `retry_backoff`, `max_retries`, `self.retry()` | `Retry(max=3, interval=[10, 30, 60])` | `max_tries`, raise `Retry(defer=...)` |
| lease / ack timing | `acks_late`, `visibility_timeout`, `task_reject_on_worker_lost` | job timeout; a "failed" registry | `job_timeout`; jobs survive worker death in Redis |
| dedupe | your own (task ids are random unless you set them) | `job_id=` | `_job_id=` (enqueue ignored if present) |
| dead letters | failed task store / your own DLQ | `FailedJobRegistry` | job result with an error |
| schedules | Celery beat | `rq-scheduler` / `rq-cron` | `cron_jobs` in settings |
| concurrency | processes (prefork), threads, gevent | one forked process per job | one asyncio loop, many jobs |

### 13.2 Celery

The most feature-rich and the most configurable (and the easiest to misconfigure):

```python
# tasks.py
from celery import Celery

app = Celery("shop", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")
app.conf.update(
    task_serializer="json", accept_content=["json"],      # never pickle
    task_acks_late=True,                                   # ack AFTER the task runs: at-least-once
    task_reject_on_worker_lost=True,                       # requeue if the worker process dies mid-task
    worker_prefetch_multiplier=1,                          # reserve one job at a time
    task_time_limit=300, task_soft_time_limit=270,         # hard and soft limits in seconds
    broker_transport_options={"visibility_timeout": 3600}, # Redis broker: redeliver after an hour without ack
)


@app.task(bind=True, autoretry_for=(ConnectionError, TimeoutError), retry_backoff=True,
          retry_backoff_max=600, retry_jitter=True, max_retries=5, acks_late=True)
def send_welcome_email(self, user_id: int) -> None:
    ...                                                    # must be idempotent (section 11)
```

Use it from the web app and the shell:

```python
from tasks import send_welcome_email

send_welcome_email.delay(42)                                         # run as soon as a worker is free
send_welcome_email.apply_async(args=[42], countdown=60)               # in a minute
```

> **Try it on your machine** (needs Redis and `pip install celery redis`; not run here):
>
> ```bash
> redis-server &                                     # or: docker run --rm -p 6379:6379 redis:7
> celery -A tasks worker --loglevel=info --concurrency=2
> python -c "from tasks import send_welcome_email; print(send_welcome_email.delay(42).id)"
> ```
>
> The worker's log shows a line when the task is **received** (with the task name, a UUID and the arguments) and a line when it **succeeded** (with the run time); `delay()` prints the task's UUID. Exact lines, UUIDs and timings differ by version and machine, so no output is shown. Stop the worker with Ctrl+C: it finishes the running task first ("warm shutdown").

Know the **defaults** of any queue library before you trust it. Celery's default acknowledges a task when it is **received** (`acks_late` off), which gives at-most-once if the worker dies mid-task. Many production setups switch `acks_late` on, accept at-least-once, and rely on idempotent tasks, exactly the trade-off of section 8.4. The Redis broker also redelivers an unacknowledged task after `visibility_timeout` (one hour by default): a task that legitimately runs longer is delivered a **second time while still running**, the lease problem of section 9. (Check the documentation of your Celery version for current defaults.)

### 13.3 RQ

The simplest: Redis only, plain Python functions, one forked "work horse" process per job, so a job cannot leak memory into the next:

```python
from redis import Redis
from rq import Queue, Retry

from jobs import send_welcome_email                        # an ordinary function in an importable module

queue = Queue("emails", connection=Redis())
queue.enqueue(send_welcome_email, 42, retry=Retry(max=3, interval=[10, 30, 60]), job_timeout=300)
```

```bash
rq worker emails          # start a worker for that queue
rq info                   # queues, workers, failed jobs
```

Failed jobs stay in the **FailedJobRegistry** for inspection and requeue, RQ's version of the dead-letter queue. It is synchronous, easy to understand, and fine when you do not need the extras.

### 13.4 arq

Built for `asyncio`: one worker process runs many I/O-bound jobs concurrently on a single event loop, which suits FastAPI projects that already use `async` code and call many HTTP APIs:

```python
# worker.py
from arq import cron
from arq.connections import RedisSettings


async def send_welcome_email(ctx, user_id: int) -> None:
    ...                                                    # ctx holds shared resources made at start-up


async def nightly_cleanup(ctx) -> None:
    ...


class WorkerSettings:
    functions = [send_welcome_email]
    cron_jobs = [cron(nightly_cleanup, hour=2, minute=0)]
    redis_settings = RedisSettings()
    max_tries = 5
    job_timeout = 300
```

```python
# in the web app
from arq import create_pool
from arq.connections import RedisSettings

redis = await create_pool(RedisSettings())
await redis.enqueue_job("send_welcome_email", 42, _job_id="welcome:42", _defer_by=60)   # a repeated _job_id is ignored while it exists
```

```bash
arq worker.WorkerSettings
```

(Check the arq documentation for the exact behaviour of `_job_id` and retries in your version.)

### 13.5 Choosing

| Choose | When |
|---|---|
| **A database-backed queue** (your own table, or a library such as Procrastinate on PostgreSQL) | modest volume; you want jobs in the same transaction as your data; fewer moving parts |
| **RQ** | simple Redis jobs, a small team, synchronous code |
| **arq** | an async codebase, many concurrent network calls per worker |
| **Celery** | many features needed (routing, workflows, schedules, many brokers), a team that can operate it |
| **Cloud queues** (SQS with a worker, Cloud Tasks, Pub/Sub) | you already run on that cloud and want the provider to run the broker |
| **Kafka** | streams of events consumed by many systems, replay, very high volume |

Whatever you pick, answer the same questions: when is a job acknowledged, what happens on a crash, how are retries and dead letters handled, what is the visibility timeout, how are duplicates prevented, how do you see the queue's depth and age. The next sections turn those questions into practice.

### Try it: read the config

In a Celery project you find `task_acks_late` unset and workers that are deployed by killing the old ones. What is the risk, and what do you change?

<details><summary>Answer</summary>

With early acks, a task that was received but not finished when a worker is killed is **lost** (at-most-once). Deployments make this routine. Set `task_acks_late = True` and `task_reject_on_worker_lost = True` so interrupted tasks are redelivered, make every task idempotent (section 11) because redelivery now means duplicates, and use `SIGTERM` for graceful shutdown so running tasks finish first.

</details>

## 14. Scheduled jobs

### 14.1 Cron expressions

Many jobs run on a **schedule**: invoices on the 1st, clean-up every night, a digest every weekday at 9:00. The standard notation is the five-field **cron** expression:

```text
 ┌───────── minute        (0-59)
 │ ┌─────── hour          (0-23)
 │ │ ┌───── day of month  (1-31)
 │ │ │ ┌─── month         (1-12)
 │ │ │ │ ┌─ day of week   (0-6, 0 = Sunday)
 │ │ │ │ │
 * * * * *
```

Each field may be `*` (every value), a number, a list (`1,15`), a range (`1-5`), or a step (`*/15`, `0-30/10`). Examples: `*/15 * * * *` every 15 minutes; `0 9 * * 1-5` at 09:00 on weekdays; `30 2 1 * *` at 02:30 on the 1st of each month. A classic quirk: if both day-of-month and day-of-week are restricted, cron runs when **either** matches.

Here is a small parser and "next run" function, so that the rules are visible and testable:

```python
# cron.py
from datetime import datetime, timedelta

FIELDS = [("minute", 0, 59), ("hour", 0, 23), ("day", 1, 31), ("month", 1, 12), ("weekday", 0, 6)]


def parse_field(text: str, low: int, high: int) -> set[int]:
    values = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, step_text = part.split("/")
            step = int(step_text)
        if part == "*":
            start, end = low, high
        elif "-" in part:
            start, end = (int(x) for x in part.split("-"))
        else:
            start = end = int(part)
            if "/" in text and part.isdigit():
                end = high                               # "5/10" means from 5 to the end
        if not (low <= start <= end <= high) or step < 1:
            raise ValueError(f"bad cron field {text!r}")
        values.update(range(start, end + 1, step))
    return values


class Cron:
    def __init__(self, expression: str):
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError("a cron expression has 5 fields")
        self.expression = expression
        self.minutes, self.hours, self.days, self.months, self.weekdays = (
            parse_field(text, low, high) for text, (_, low, high) in zip(parts, FIELDS))
        self.day_restricted, self.weekday_restricted = parts[2] != "*", parts[4] != "*"

    def _day_matches(self, d: datetime) -> bool:
        dom_ok = d.day in self.days
        dow_ok = (d.weekday() + 1) % 7 in self.weekdays          # Python: Monday=0; cron: Sunday=0
        if self.day_restricted and self.weekday_restricted:
            return dom_ok or dow_ok                              # the classic "either" rule
        return dom_ok and dow_ok

    def next_after(self, after: datetime) -> datetime:
        """The first matching minute strictly after `after`."""
        day = after.replace(hour=0, minute=0, second=0, microsecond=0)
        for _ in range(366 * 5):
            if day.month in self.months and self._day_matches(day):
                for hour in sorted(self.hours):
                    for minute in sorted(self.minutes):
                        candidate = day.replace(hour=hour, minute=minute)
                        if candidate > after:
                            return candidate
            day += timedelta(days=1)
        raise ValueError(f"no run time within 5 years for {self.expression!r}")

    def between(self, start: datetime, end: datetime):
        """Every run time t with start < t <= end."""
        t = self.next_after(start)
        while t <= end:
            yield t
            t = self.next_after(t)
```

```python run
from datetime import datetime

from cron import Cron

now = datetime(2026, 11, 6, 9, 0)                        # a Friday
print("2026-11-06 is a", now.strftime("%A"))
for expression in ["*/15 * * * *", "0 9 * * 1-5", "30 2 1 * *", "0 0 29 2 *", "0 8 13 * 5"]:
    c = Cron(expression)
    nxt = c.next_after(now)
    print(f"{expression:14} next after Fri 09:00 -> {nxt:%a %Y-%m-%d %H:%M}")
print("every 15 min between 10:00 and 11:00:", [f"{t:%H:%M}" for t in Cron("*/15 * * * *").between(datetime(2026, 11, 6, 10, 0), datetime(2026, 11, 6, 11, 0))])
```
```text
2026-11-06 is a Friday
*/15 * * * *   next after Fri 09:00 -> Fri 2026-11-06 09:15
0 9 * * 1-5    next after Fri 09:00 -> Mon 2026-11-09 09:00
30 2 1 * *     next after Fri 09:00 -> Tue 2026-12-01 02:30
0 0 29 2 *     next after Fri 09:00 -> Tue 2028-02-29 00:00
0 8 13 * 5     next after Fri 09:00 -> Fri 2026-11-13 08:00
every 15 min between 10:00 and 11:00: ['10:15', '10:30', '10:45', '11:00']
```

(`0 8 13 * 5` is "the 13th of the month **or** any Friday": the next Friday is 2026-11-13, which is both.) In practice you use a library or your platform's scheduler instead of your own parser, but you must know the rules to read a schedule correctly.

### 14.2 Time zones and daylight saving time

A schedule written in a local time zone behaves strangely twice a year. On the day clocks go **forward**, a time like 02:30 does not exist; on the day they go **back**, 01:30 happens **twice**. A job "at 02:30" can be skipped, or run twice:

```python run
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ny = ZoneInfo("America/New_York")
spring = datetime(2026, 3, 8, 2, 30, tzinfo=ny)
print("local 02:30 on 2026-03-08 (clocks jumped from 02:00 to 03:00):")
print("   converted to UTC and back:", spring.astimezone(timezone.utc).astimezone(ny).strftime("%H:%M"), "<- the hour 02:xx does not exist")

first = datetime(2026, 11, 1, 1, 30, tzinfo=ny, fold=0)
second = datetime(2026, 11, 1, 1, 30, tzinfo=ny, fold=1)
print("local 01:30 on 2026-11-01 (clocks go back at 02:00) happens twice:")
print("   first  :", first.astimezone(timezone.utc).strftime("%H:%M UTC"), "| second:", second.astimezone(timezone.utc).strftime("%H:%M UTC"))
```
```text
local 02:30 on 2026-03-08 (clocks jumped from 02:00 to 03:00):
   converted to UTC and back: 03:30 <- the hour 02:xx does not exist
local 01:30 on 2026-11-01 (clocks go back at 02:00) happens twice:
   first  : 05:30 UTC | second: 06:30 UTC
```

Rules of thumb: **store and schedule in UTC** for technical jobs; use a local zone only for jobs that must follow a clock on the wall (a 9:00 digest), and then decide what "skipped" and "doubled" days mean for that job. Always test the two transition days. (Keep the `tzdata` package in your dependencies on Windows, core.17.)

### 14.3 The four classic problems

| Problem | Example | Defence |
|---|---|---|
| **Overlap** | the hourly job takes 70 minutes; runs pile up | a lock or a state check: skip or delay if the previous run is still going |
| **Missed runs** | the scheduler was down from 10:00 to 11:07 | a **misfire policy**: run once on recovery, run every missed time, or skip; chosen per job |
| **Duplicate runs** | three app servers each run a scheduler | one scheduler (leader), or **idempotent scheduling** (below) |
| **Time zones / DST** | 02:30 runs twice or never | schedule in UTC; test the transition days |

A very effective trick is **idempotent scheduling**: the scheduler does not "run" the job; it **enqueues a job whose dedupe key contains the scheduled time** (`nightly-digest:2026-11-06T09:00`). However many scheduler instances run, and however many times a restarted scheduler re-examines the same period, the unique key ensures exactly one job per scheduled time:

```python
# scheduler.py
from datetime import datetime, timedelta

from cron import Cron


class Entry:
    def __init__(self, name, cron_expression, kind, payload=None, queue="default"):
        self.name, self.cron, self.kind, self.payload, self.queue = name, Cron(cron_expression), kind, payload or {}, queue


class Scheduler:
    """Turns schedules into queued jobs. Safe to run in many copies, and safe to restart."""

    def __init__(self, job_queue, entries, start: datetime, misfire="latest"):
        self.queue, self.entries, self.cursor, self.misfire = job_queue, entries, start, misfire

    def tick(self, now: datetime) -> int:
        enqueued = 0
        for e in self.entries:
            due = list(e.cron.between(self.cursor, now))               # scheduled times in (cursor, now]
            if self.misfire == "latest":
                due = due[-1:]                                         # catch up with ONE run
            elif self.misfire == "skip":
                due = [t for t in due if now - t < timedelta(minutes=1)]
            for t in due:
                stamp = t.isoformat(timespec="minutes")
                self.queue.enqueue(e.kind, {**e.payload, "scheduled_for": stamp}, queue=e.queue,
                                   dedupe_key=f"{e.name}:{stamp}")      # the idempotency key IS the schedule slot
                enqueued += 1
        self.cursor = now
        return enqueued
```

```python run
import os
import tempfile
import threading
from contextlib import closing
from datetime import datetime, timedelta

from jobqueue import JobQueue
from scheduler import Entry, Scheduler

start = datetime(2026, 11, 6, 10, 0)


def job_count(q):
    with closing(q._connect()) as db:
        return db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]


with tempfile.TemporaryDirectory() as tmp:
    # 1. one scheduler ticking every minute for an hour
    q = JobQueue(os.path.join(tmp, "a.db"))
    s = Scheduler(q, [Entry("digest", "*/15 * * * *", "digest")], start)
    for minute in range(1, 61):
        s.tick(start + timedelta(minutes=minute))
    print("one scheduler, 1 hour           : jobs =", job_count(q), "(10:15, 10:30, 10:45, 11:00)")

    # 2. three scheduler processes at once: still one job per slot
    q = JobQueue(os.path.join(tmp, "b.db"))
    entries = lambda: [Entry("digest", "*/15 * * * *", "digest")]
    schedulers = [Scheduler(q, entries(), start) for _ in range(3)]

    def run(s):
        for minute in range(1, 61):
            s.tick(start + timedelta(minutes=minute))

    threads = [threading.Thread(target=run, args=(s,)) for s in schedulers]
    for t in threads: t.start()
    for t in threads: t.join()
    print("three schedulers at the same time: jobs =", job_count(q), "<- not 12")

    # 3. downtime: the scheduler was off from 10:00 to 11:07; compare misfire policies
    for policy in ("latest", "all", "skip"):
        q = JobQueue(os.path.join(tmp, f"c-{policy}.db"))
        s = Scheduler(q, [Entry("digest", "*/15 * * * *", "digest")], start, misfire=policy)
        s.tick(datetime(2026, 11, 6, 11, 7))
        print(f"restart at 11:07, misfire={policy:6}: jobs =", job_count(q))
```
```text
one scheduler, 1 hour           : jobs = 4 (10:15, 10:30, 10:45, 11:00)
three schedulers at the same time: jobs = 4 <- not 12
restart at 11:07, misfire=latest: jobs = 1
restart at 11:07, misfire=all   : jobs = 4
restart at 11:07, misfire=skip  : jobs = 0
```

The right misfire policy depends on the job: a nightly report should run **once** on recovery (`latest`); a job that processes "everything since the last run" is fine with `all` or `latest`; a per-minute metrics ping should `skip` old slots.

### 14.4 Tools

| Tool | Notes |
|---|---|
| **cron / systemd timers** | simple, one machine; no retries or visibility; the host is a single point of failure |
| **Kubernetes `CronJob`** | `concurrencyPolicy: Forbid` stops overlap; `startingDeadlineSeconds` bounds the catch-up |
| **Celery beat**, **arq `cron_jobs`**, **rq-scheduler**, **APScheduler** | schedule inside the app stack; run **exactly one** beat/scheduler instance, or use idempotent keys as above |
| **Cloud schedulers** (EventBridge, Cloud Scheduler) | call an HTTP endpoint or put a message on a queue at the time |

A good habit: the schedule only **enqueues** work. The job itself runs on the normal worker pool with retries, dead letters and metrics, exactly like any other job.

### Try it: next run

What is the next run of `0 9 * * 1-5` after Friday 2026-11-06 09:00? And of `30 2 * * *` if the server's time zone has a DST jump at 02:00 that night?

<details><summary>Answer</summary>

Monday 2026-11-09 at 09:00 (weekdays only; the weekend is skipped). For `30 2 * * *` on the night the clocks jump from 02:00 to 03:00, 02:30 does not exist, so the job is skipped or runs at an odd moment depending on the scheduler; on the night clocks go back it can run twice. Schedule technical jobs in UTC to avoid both.

</details>

### Try it: three schedulers

Why does the `dedupe_key` contain the scheduled time and not the job's name only?

<details><summary>Answer</summary>

With the name only (`digest`) the second tick of the day would be ignored as a duplicate of the first, and the digest would run once ever. The key must identify **one slot of one schedule**: name plus the scheduled time. Then every scheduler computes the same key for the same slot, so exactly one job is created, while the next slot has a new key and creates a new job.

</details>


## 15. Operating caches and queues

A system with a cache and a queue has **hidden state**: values in a cache, jobs waiting in a queue, workers that may or may not be alive. Nothing fails loudly when that state goes wrong; things just get slower or older. So you must put numbers on the hidden state and watch them.

### 15.1 What to measure

**Queue health**

| Metric | Why it matters |
|---|---|
| **Queue depth** (jobs ready to run) | a growing number means workers cannot keep up |
| **Age of the oldest ready job** | the best single metric: it is the delay your users actually feel, and it catches a stuck worker pool that produces no errors |
| **Jobs running** vs worker count | are the workers busy, idle or missing? |
| **Throughput** (jobs completed per minute) | zero while the queue has jobs means the workers are stuck or dead |
| **Failure and retry rate** | a rising rate points at a broken dependency or a bad deploy |
| **Dead-letter count** | any non-zero value is work that needs a human |
| **Redeliveries** (lease expirations) | many of these mean crashes or leases that are too short |
| **Job duration** (median and 95th percentile) | slow jobs hold capacity and expire leases |

**Cache health**: hit ratio (section 2), eviction count, memory used against the limit, command latency, connected clients, number of keys, and the database load behind the cache.

```python
# opsmetrics.py
def prometheus_text(job_queue, queue="default") -> str:
    """The text format that Prometheus (and many other tools) scrape from a /metrics endpoint."""
    stats = job_queue.stats(queue)
    lines = [f'jobs{{queue="{queue}",state="{state}"}} {stats[state]}' for state in ("queued", "running", "done", "dead")]
    lines.append(f'oldest_ready_job_age_seconds{{queue="{queue}"}} {stats["oldest_ready_age"]}')
    return "\n".join(lines)


def health(stats: dict, *, max_age=60.0, previous_done=None) -> list[str]:
    """Turn the numbers into alerts a human can act on."""
    alerts = []
    if stats["dead"] > 0:
        alerts.append(f"{stats['dead']} job(s) in the dead-letter state")
    if stats["oldest_ready_age"] > max_age:
        alerts.append(f"the oldest ready job has waited {stats['oldest_ready_age']:.0f} s (limit {max_age:.0f} s)")
    if previous_done is not None and stats["done"] == previous_done and stats["queued"] > 0:
        alerts.append("jobs are waiting but none completed since the last check: workers stuck or gone")
    return alerts
```

```python run
import os
import tempfile

from jobqueue import JobQueue
from opsmetrics import health, prometheus_text
from worker import Worker

with tempfile.TemporaryDirectory() as tmp:
    clock = [0.0]
    q = JobQueue(os.path.join(tmp, "q.db"), now=lambda: clock[0])
    w = Worker(q, {"task": lambda payload, job: None})

    print("--- healthy: workers keep up ---")
    for _ in range(5):
        q.enqueue("task", {})
    while w.run_once():
        pass
    done_before = q.stats()["done"]
    print(prometheus_text(q))
    print("alerts:", health(q.stats(), previous_done=None) or "none")

    print("\n--- backlog: 50 jobs arrive and nobody is working ---")
    for _ in range(50):
        q.enqueue("task", {})
    clock[0] += 120
    print("alerts:", health(q.stats(), previous_done=done_before))

    print("\n--- a poison job ---")
    q.enqueue("mystery-kind", {})
    clock[0] += 1
    while w.run_once():
        pass
    print("alerts:", health(q.stats(), previous_done=done_before))
```
```text
--- healthy: workers keep up ---
jobs{queue="default",state="queued"} 0
jobs{queue="default",state="running"} 0
jobs{queue="default",state="done"} 5
jobs{queue="default",state="dead"} 0
oldest_ready_job_age_seconds{queue="default"} 0.0
alerts: none

--- backlog: 50 jobs arrive and nobody is working ---
alerts: ['the oldest ready job has waited 120 s (limit 60 s)', 'jobs are waiting but none completed since the last check: workers stuck or gone']

--- a poison job ---
alerts: ['1 job(s) in the dead-letter state']
```

Page a human for conditions that need action (the oldest job is too old, the dead-letter queue is not empty, nothing completed while work is waiting) and put the rest on a dashboard. Alert on **symptoms users feel** (job age), not on every cause.

### 15.2 Follow one action across the web app and the worker

A user clicks "Export report"; the API creates a job; a worker runs it an hour later. When something goes wrong you need to connect those three events. Put a **request id** (swe.09 returns to this) into the job, and write it, with the job id and the attempt number, in every log line the worker writes. JSON logs make this searchable:

```python run
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
log = logging.getLogger("worker")


def log_event(event, **fields):
    log.info(json.dumps({"event": event, **fields}, sort_keys=True))


request_id = f"req-{12345:08x}"                       # in real life: made by a middleware, one per HTTP request
log_event("job_enqueued", job_id=41, kind="report", request_id=request_id)          # written by the web app
payload = {"month": "2026-10", "_meta": {"request_id": request_id}}                  # travels inside the job

log_event("job_started", job_id=41, attempt=1, request_id=payload["_meta"]["request_id"])    # written by the worker, later
log_event("job_failed", job_id=41, attempt=1, request_id=payload["_meta"]["request_id"], error="ConnectionError", will_retry_in=2.5)
log_event("job_finished", job_id=41, attempt=2, request_id=payload["_meta"]["request_id"], seconds=0.83)
```
```text
{"event": "job_enqueued", "job_id": 41, "kind": "report", "request_id": "req-00003039"}
{"attempt": 1, "event": "job_started", "job_id": 41, "request_id": "req-00003039"}
{"attempt": 1, "error": "ConnectionError", "event": "job_failed", "job_id": 41, "request_id": "req-00003039", "will_retry_in": 2.5}
{"attempt": 2, "event": "job_finished", "job_id": 41, "request_id": "req-00003039", "seconds": 0.83}
```

Searching the logs for `req-00003039` now returns the whole story: the click, the first failure and the retry that succeeded. Never log the payload blindly (it may hold personal data, swe.07 section 15.6).

### 15.3 How many workers? Little's law

**Little's law** relates three numbers in any stable system: *average number of jobs in the system* = *arrival rate* x *average time each spends there*. For workers: **busy workers = jobs per second x seconds per job**. It gives a first estimate of capacity:

```python run
import math


def workers_needed(jobs_per_second, seconds_per_job, headroom=0.3):
    busy = jobs_per_second * seconds_per_job
    return busy, math.ceil(busy * (1 + headroom))


def drain_seconds(backlog, arrival_rate, capacity):
    return float("inf") if capacity <= arrival_rate else backlog / (capacity - arrival_rate)


busy, workers = workers_needed(20, 0.5)
print(f"20 jobs/s x 0.5 s each = {busy:.0f} workers busy on average -> run about {workers} with 30% headroom")

capacity = workers / 0.5                                  # jobs per second the pool can finish
print(f"that pool finishes {capacity:.0f} jobs/s")

backlog = (100 - capacity) * 60                           # a burst: 100 jobs/s for one minute
print(f"a one-minute burst of 100 jobs/s leaves a backlog of {backlog:.0f} jobs")
seconds = drain_seconds(backlog, arrival_rate=20, capacity=capacity)
print(f"back at 20 jobs/s, the backlog drains in {seconds / 60:.0f} minutes")
print("a pool of exactly 'average' size (10 workers = 20 jobs/s) never drains it:", drain_seconds(backlog, 20, 20))
```
```text
20 jobs/s x 0.5 s each = 10 workers busy on average -> run about 13 with 30% headroom
that pool finishes 26 jobs/s
a one-minute burst of 100 jobs/s leaves a backlog of 4440 jobs
back at 20 jobs/s, the backlog drains in 12 minutes
a pool of exactly 'average' size (10 workers = 20 jobs/s) never drains it: inf
```

The lessons: size for the **average plus headroom**, not the average (with no spare capacity a backlog never shrinks); decide how long a burst may take to clear (that is your latency promise); and **autoscale on the age of the oldest job**, not on CPU. Real jobs vary in length, so use measured percentiles instead of one average.

### 15.4 Backpressure: saying no on purpose

A queue absorbs spikes, but not without limit. If producers outrun workers for long enough, the queue grows until storage runs out, and the oldest jobs become useless. **Backpressure** means refusing or slowing new work when the system is overloaded:

```python run
import os
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from jobqueue import JobQueue

with tempfile.TemporaryDirectory() as tmp:
    q = JobQueue(os.path.join(tmp, "q.db"))
    MAX_WAITING = 3
    app = FastAPI()

    @app.post("/exports", status_code=202)
    def export():
        stats = q.stats()
        if stats["queued"] >= MAX_WAITING:                                     # the queue is full
            raise HTTPException(503, "busy, try again shortly", headers={"Retry-After": "30"})
        return {"job_id": q.enqueue("export", {})}

    c = TestClient(app)
    answers = [c.post("/exports") for _ in range(5)]
    print([r.status_code for r in answers])
    print("Retry-After on the refusal:", answers[-1].headers["retry-after"], "seconds")
```
```text
[202, 202, 202, 503, 503]
Retry-After on the refusal: 30 seconds
```

Options, from gentle to firm: bound the queue and answer `503`/`429` with `Retry-After`; give each tenant a share (rate limits per user, swe.07 section 11); put low-priority work on its own queue; drop work that has gone stale (a job older than its usefulness is deleted, not run); scale workers up. Whatever you choose, decide it **before** the day it happens.

### 15.5 A cache outage must not become an application outage

Redis will restart one day. If every cache call raises `ConnectionError`, a pure speed-up has become a single point of failure. Treat the cache as **optional**: short timeouts, treat errors as misses, and stop calling it for a moment after a failure so that every request does not wait for a timeout:

```python run
import time

from miniredis import MiniRedis


class FlakyRedis(MiniRedis):
    down = False

    def get(self, key):
        if self.down:
            raise ConnectionError("cache unreachable")
        return super().get(key)


class SafeCache:
    def __init__(self, redis, pause=5.0, now=time.monotonic):
        self.redis, self.pause, self.now, self.skip_until = redis, pause, now, 0.0
        self.errors = 0

    def get(self, key):
        if self.now() < self.skip_until:
            return None                                     # recently failed: do not even try
        try:
            return self.redis.get(key)
        except (ConnectionError, TimeoutError):
            self.errors += 1
            self.skip_until = self.now() + self.pause
            return None                                     # behave as a miss: the caller falls back to the database

clock = [0.0]
redis = FlakyRedis()
redis.set("k", "cached value")
cache = SafeCache(redis, now=lambda: clock[0])
print("cache up        :", cache.get("k"))
redis.down = True
print("cache goes down :", cache.get("k"), "(a miss; the app reads the database instead)")
print("next 3 calls    :", [cache.get("k") for _ in range(3)], "| real attempts so far:", cache.errors, "<- not hammering a dead server")
redis.down = False
clock[0] += 6
print("after the pause :", cache.get("k"))
```
```text
cache up        : cached value
cache goes down : None (a miss; the app reads the database instead)
next 3 calls    : [None, None, None] | real attempts so far: 1 <- not hammering a dead server
after the pause : cached value
```

Then check what the **database** does when the cache is empty: if it cannot survive the full load, a cache restart is an outage (section 6). Protect it with rate limits, single flight and a warm-up plan. Operating notes for Redis itself: never run `KEYS *` in production (it blocks the server; use `SCAN`); set a `maxmemory` and an eviction policy that fits (a cache evicts, a queue or session store must not); understand what persistence you configured and what a restart loses.

### 15.6 Deployments and workers

- Send `SIGTERM`, let workers **drain** (finish the current job) and give them time before `SIGKILL` (section 10.2).
- **Version skew:** old jobs meet new code and new jobs meet old workers during a rolling deploy. Keep payloads backward compatible (add fields; do not rename) and migrate the database before starting new workers.
- Provide a way to **pause** a queue and to **inspect** and **redrive** the dead-letter state (an admin page or a command), before you need it at 3 a.m.
- Test recovery **on purpose**: restart a worker while it is busy, kill one with `SIGKILL`, stop the broker for a minute. The project below does the first two automatically.

### Try it: read the dashboard

Depth 12,000 and growing; oldest ready job 25 minutes; 0 errors; 8 workers running; throughput 0 jobs/min. What is happening and what do you check?

<details><summary>Answer</summary>

No errors but zero throughput and a very old job: the workers are alive but **stuck**: blocked on a dependency, deadlocked, or waiting on a lock, or a very slow job occupies them all. Check what the running jobs are doing (thread dumps, logs for the last "job_started" without a "job_finished"), whether a downstream service is hanging without timeouts, and whether one poison job is taking every worker in turn. Add per-job time limits and alert on "waiting jobs but nothing completing".

</details>

### Try it: size a pool

Reports arrive at 2 per second and each takes 3 seconds. How many workers do you need, with 50% headroom? What happens with 5?

<details><summary>Answer</summary>

2 x 3 = 6 busy workers on average; with 50% headroom, 9. With 5 workers the capacity is 5 / 3 = 1.67 reports per second, below the arrival rate of 2, so the queue grows by about 0.33 jobs per second for as long as the traffic lasts (and never recovers by itself). Anything below the average load is a guaranteed backlog.

</details>

## 16. Project: an e-mail and report worker that survives crashes

This is the second outcome of the chapter: **build a worker system that survives being killed.** We assemble everything: the durable queue, leases, an idempotent report job, an idempotent e-mail job, an API that is safe to call twice, a real worker **process**, and tests that kill that process in the nastiest places.

### 16.1 The rules

1. Staff request a monthly report with `POST /reports`. The API answers `202` immediately. Asking for the same month twice creates **one** job. Invalid months are refused at the door.
2. A worker builds the report as a CSV file, **deterministically**, and **publishes it atomically** (readers never see half a file).
3. When the report is ready, the system sends **one** e-mail to finance, no matter what crashes or repeats.
4. Killing a worker at **any moment** (`SIGKILL`, a power cut) loses nothing: after a restart the report exists and the e-mail went out exactly once.
5. A bad job goes to the dead state and does not block others. A graceful stop (`SIGTERM`) finishes the running job.

```text
 POST /reports --> API ---(one transaction)---> shop.db: reports row + jobs row
                                                   |
                      worker process (kill it any time; start another)
                         |  reserve with a lease
                         |  report job : orders -> deterministic CSV -> atomic publish -> status ready
                         |                                           + report_email job (same transaction)
                         |  email job  : claim -> provider.send(idempotency key) -> record
                         v
                 out/report-2026-10.csv        provider.db (the "external" e-mail service)
```

### 16.2 The pieces you already have

Copy these from earlier sections into one project folder: `jobqueue.py` (section 9), `worker.py` (section 10), `reports.py` (section 11.8). Everything else is new. The project is a normal folder of files, run with `python`, tested with `pytest`.

### 16.3 The external service, the tasks, the API and the worker process

The fake e-mail provider keeps its memory **in a file**, because a real e-mail service survives the death of your worker, and an in-memory fake would forget everything at the wrong moment. Like real providers it honours an idempotency key:

```python
# provider.py
import sqlite3
from contextlib import closing


class SqliteMailProvider:
    """A fake e-mail service whose memory lives in a file, so it survives the death of our worker process.
    Like real providers it honours an idempotency key: the same key never produces a second message."""

    def __init__(self, path):
        self.path = path
        with closing(self._connect()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "idempotency_key TEXT UNIQUE, to_addr TEXT, subject TEXT)")

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10, isolation_level=None)

    def send(self, to, subject, idempotency_key):
        with closing(self._connect()) as db:
            db.execute("INSERT INTO messages (idempotency_key, to_addr, subject) VALUES (?, ?, ?) "
                       "ON CONFLICT (idempotency_key) DO NOTHING", (idempotency_key, to, subject))
            return db.execute("SELECT id FROM messages WHERE idempotency_key = ?", (idempotency_key,)).fetchone()[0]

    def count(self):
        with closing(self._connect()) as db:
            return db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
```

The task handlers: this is where the idempotency decisions of section 11 live. Read every `crash.hit(...)` line as "the process may die exactly here":

```python
# tasks.py
import os
import re
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass

from jobqueue import JobQueue
from provider import SqliteMailProvider
from reports import build_report, digest, write_atomic
from worker import PermanentError

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders  (id INTEGER PRIMARY KEY, customer TEXT, month TEXT, total_cents INTEGER);
CREATE TABLE IF NOT EXISTS reports (month TEXT PRIMARY KEY, status TEXT NOT NULL, digest TEXT, requested_at REAL);
CREATE TABLE IF NOT EXISTS email_log (key TEXT PRIMARY KEY, to_addr TEXT, state TEXT, provider_id TEXT);
"""
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@dataclass
class Context:
    db_path: str
    out_dir: str
    provider_db: str
    recipient: str = "finance@example.com"


class EnvCrash:
    """Test hook: when the environment variable CRASH_AT names this point, the process dies on the spot,
    like a power cut. os._exit skips every `finally`, `with` and cleanup handler."""

    def __init__(self, prefix=""):
        self.prefix = prefix

    def hit(self, point):
        name = f"{self.prefix}:{point}" if self.prefix else point
        if os.environ.get("CRASH_AT") == name:
            os._exit(137)


def init_db(path):
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.executescript(SCHEMA)


def seed_orders(path):
    rows = [(1, "ada", "2026-10", 2500), (2, "bo", "2026-10", 4200), (3, "cy", "2026-10", 990), (4, "ada", "2026-09", 1500)]
    with closing(sqlite3.connect(path, isolation_level=None)) as db:
        db.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)", rows)


def orders_for(ctx, month):
    with closing(sqlite3.connect(ctx.db_path, isolation_level=None)) as db:
        return [tuple(r) for r in db.execute("SELECT id, customer, total_cents FROM orders WHERE month = ?", (month,))]


def make_report_handler(ctx, queue):
    def handler(payload, job):
        month = payload["month"]
        if not MONTH.match(month):
            raise PermanentError(f"invalid month {month!r}")
        crash = EnvCrash()
        if os.environ.get("SENTINEL_DIR"):                                       # lets a test know the job is running
            open(os.path.join(os.environ["SENTINEL_DIR"], f"started-{job['id']}-{job['attempts']}"), "w").close()
        time.sleep(float(os.environ.get("SLOW_SECONDS", "0")))                    # stands in for heavy work
        data = build_report(orders_for(ctx, month), month)
        path = os.path.join(ctx.out_dir, f"report-{month}.csv")
        write_atomic(path, data, crash=EnvCrash("report"))                        # crash points: report:mid-write, report:before-replace
        crash.hit("report:after-replace")
        file_digest = digest(path)
        with closing(queue._connect()) as db:                                     # status AND follow-up job in ONE transaction
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE reports SET status = 'ready', digest = ? WHERE month = ?", (file_digest, month))
            queue.enqueue_in(db, "report_email", {"month": month}, dedupe_key=f"report-email:{month}")
            db.execute("COMMIT")
        crash.hit("report:after-status")
    return handler


def make_email_handler(ctx):
    provider = SqliteMailProvider(ctx.provider_db)

    def handler(payload, job):
        month, key = payload["month"], f"report-ready:{payload['month']}"
        crash = EnvCrash("email")
        with closing(sqlite3.connect(ctx.db_path, timeout=10, isolation_level=None)) as db:
            row = db.execute("SELECT state FROM email_log WHERE key = ?", (key,)).fetchone()
            if row and row[0] == "sent":
                return                                                           # already done: a duplicate delivery
            db.execute("INSERT OR IGNORE INTO email_log (key, to_addr, state) VALUES (?, ?, 'sending')", (key, ctx.recipient))
            crash.hit("after-claim")
            message_id = provider.send(ctx.recipient, f"Your report for {month} is ready", idempotency_key=key)
            crash.hit("after-send")
            db.execute("UPDATE email_log SET state = 'sent', provider_id = ? WHERE key = ?", (str(message_id), key))
            crash.hit("after-record")
    return handler


def handlers(ctx):
    queue = JobQueue(ctx.db_path)
    return {"report": make_report_handler(ctx, queue), "report_email": make_email_handler(ctx)}
```

Look at what each handler does about each crash window:

| Handler step | If the process dies right after it |
|---|---|
| builds the CSV in memory | nothing visible happened; the retry redoes it |
| `write_atomic` writes a temporary file | the final name is untouched; a stale `.tmp` file is harmless |
| `os.replace` publishes the file | the file is complete; the retry rewrites identical bytes |
| status update and the e-mail **job** in one transaction | either both exist or neither does (outbox, section 11.7) |
| e-mail handler `INSERT OR IGNORE ... 'sending'` | the retry sees `sending` and continues |
| `provider.send(..., idempotency_key=key)` | the retry sends the same key; the provider refuses a second message |
| log marked `sent` | a duplicate delivery returns at once |

The API creates the report row and the job in one transaction and is safe to call twice (the `dedupe_key` is the report month):

```python
# app.py
import re
from contextlib import closing

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from jobqueue import JobQueue

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


class ReportRequest(BaseModel):
    month: str = Field(pattern=MONTH_PATTERN)


def create_app(db_path: str) -> FastAPI:
    app, queue = FastAPI(), JobQueue(db_path)

    @app.post("/reports", status_code=202)
    def request_report(body: ReportRequest):
        with closing(queue._connect()) as db:
            db.execute("BEGIN IMMEDIATE")                      # the report row and the job commit together (outbox)
            db.execute("INSERT OR IGNORE INTO reports (month, status, requested_at) VALUES (?, 'queued', ?)", (body.month, queue.now()))
            queue.enqueue_in(db, "report", {"month": body.month}, dedupe_key=f"report:{body.month}")
            db.execute("COMMIT")
            row = db.execute("SELECT status FROM reports WHERE month = ?", (body.month,)).fetchone()
        return {"month": body.month, "status": row["status"], "status_url": f"/reports/{body.month}"}

    @app.get("/reports/{month}")
    def report_status(month: str):
        if not re.match(MONTH_PATTERN, month):
            raise HTTPException(422, "month must look like 2026-10")
        with closing(queue._connect()) as db:
            row = db.execute("SELECT month, status, digest FROM reports WHERE month = ?", (month,)).fetchone()
        if row is None:
            raise HTTPException(404, "no such report")
        return dict(row)

    return app
```

The worker process. It installs signal handlers so that `SIGTERM` means "finish the current job, then stop":

```python
# worker_main.py
"""A worker process: python worker_main.py --db shop.db --out out --provider-db provider.db"""
import argparse
import os

import tasks
from jobqueue import JobQueue
from worker import Worker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--provider-db", required=True)
    parser.add_argument("--lease", type=float, default=30.0)
    parser.add_argument("--exit-when-idle", action="store_true", help="stop when no job is queued or running (for tests)")
    args = parser.parse_args()

    ctx = tasks.Context(args.db, args.out, args.provider_db)
    queue = JobQueue(args.db)
    worker = Worker(queue, tasks.handlers(ctx), name=f"worker-{os.getpid()}", lease=args.lease)
    worker.install_signal_handlers()                       # SIGTERM / Ctrl+C: finish the current job, then stop
    while not worker.stopping.is_set():
        if worker.run_once() is None:
            stats = queue.stats()
            if args.exit_when_idle and stats["queued"] == 0 and stats["running"] == 0:
                break
            worker.stopping.wait(0.1)


if __name__ == "__main__":
    main()
```

### 16.4 Watch it survive `kill -9`

Before the tests, see it once. The next script starts a real worker process on a job that takes 30 seconds, waits until the job has started, **kills the process with `SIGKILL`**, and then starts a second worker. (Process ids and temporary folders differ on your machine; the exit code `-9` is how Python reports death by `SIGKILL` on Linux and macOS.)

```python run
import os
import subprocess
import sys
import tempfile
import time
from contextlib import closing

from fastapi.testclient import TestClient

import tasks
from app import create_app
from jobqueue import JobQueue
from provider import SqliteMailProvider

with tempfile.TemporaryDirectory() as tmp:
    db, provider_db, out = os.path.join(tmp, "shop.db"), os.path.join(tmp, "provider.db"), os.path.join(tmp, "out")
    os.mkdir(out)
    tasks.init_db(db)
    tasks.seed_orders(db)
    queue = JobQueue(db)

    def states():
        with closing(queue._connect()) as conn:
            return {r["kind"]: f"{r['state']} (attempt {r['attempts']})" for r in conn.execute("SELECT kind, state, attempts FROM jobs")}

    def worker(slow):
        env = dict(os.environ, SLOW_SECONDS=str(slow), SENTINEL_DIR=out)
        env.pop("CRASH_AT", None)
        return subprocess.Popen([sys.executable, "worker_main.py", "--db", db, "--out", out, "--provider-db", provider_db,
                                 "--lease", "1.5", "--exit-when-idle"], env=env)

    client = TestClient(create_app(db))
    print("1. request     :", client.post("/reports", json={"month": "2026-10"}).json())

    first = worker(slow=30)
    while not any(name.startswith("started-") for name in os.listdir(out)):
        time.sleep(0.05)
    print("2. worker 1    : running the job ->", states())

    first.kill()                                               # SIGKILL: no cleanup of any kind
    first.wait()
    print("3. kill -9     : exit code", first.returncode, "| report file exists:", os.path.exists(os.path.join(out, "report-2026-10.csv")))
    print("   job state   :", states(), "<- nobody told the queue; the lease is still ticking")

    second = worker(slow=0)
    second.wait(timeout=30)
    print("4. worker 2    : exit code", second.returncode, "->", states())
    path = os.path.join(out, "report-2026-10.csv")
    print("5. result      : report", os.path.getsize(path), "bytes |", SqliteMailProvider(provider_db).count(), "e-mail sent")
    print("   report row  :", client.get("/reports/2026-10").json()["status"])
    print(open(path).read().strip())
```
```text
1. request     : {'month': '2026-10', 'status': 'queued', 'status_url': '/reports/2026-10'}
2. worker 1    : running the job -> {'report': 'running (attempt 1)'}
3. kill -9     : exit code -9 | report file exists: False
   job state   : {'report': 'running (attempt 1)'} <- nobody told the queue; the lease is still ticking
4. worker 2    : exit code 0 -> {'report': 'done (attempt 2)', 'report_email': 'done (attempt 1)'}
5. result      : report 90 bytes | 1 e-mail sent
   report row  : ready
month,order_id,customer,total_cents
2026-10,1,ada,2500
2026-10,2,bo,4200
2026-10,3,cy,990
```

The first worker died holding the job. Nothing was published and the queue had no idea, until the **lease ran out**. The second worker then took the job (attempt 2), published the report atomically and sent the e-mail once. That is the whole mechanism of the chapter in one run.

### 16.5 The tests: kill it everywhere

`kill -9` at a random moment is a good demonstration and a poor test: it depends on timing. The tests below add deterministic **crash points** inside the handlers (`CRASH_AT=email:after-send` makes the worker call `os._exit(137)` at exactly that line) and run a second worker afterwards. Seven crash points, each followed by a restart, plus the `SIGKILL` run, a `SIGTERM` run, duplicate requests and a poison job:

```python
# test_survival.py
import os
import signal
import subprocess
import sys
import time
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

import tasks
from app import create_app
from jobqueue import JobQueue
from provider import SqliteMailProvider
from reports import build_report, digest

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED = build_report([(1, "ada", 2500), (2, "bo", 4200), (3, "cy", 990)], "2026-10")


class Env:
    def __init__(self, tmp_path):
        self.db = str(tmp_path / "shop.db")
        self.provider_db = str(tmp_path / "provider.db")
        self.out = tmp_path / "out"
        self.out.mkdir()
        tasks.init_db(self.db)
        tasks.seed_orders(self.db)
        self.queue = JobQueue(self.db)
        self.client = TestClient(create_app(self.db))
        self.report_path = self.out / "report-2026-10.csv"

    def start_worker(self, *, crash_at=None, slow=0.0, lease=1.0, exit_when_idle=True, sentinel=False):
        env = dict(os.environ, SLOW_SECONDS=str(slow))
        env.pop("CRASH_AT", None)
        if crash_at:
            env["CRASH_AT"] = crash_at
        if sentinel:
            env["SENTINEL_DIR"] = str(self.out)
        cmd = [sys.executable, os.path.join(HERE, "worker_main.py"), "--db", self.db, "--out", str(self.out),
               "--provider-db", self.provider_db, "--lease", str(lease)]
        if exit_when_idle:
            cmd.append("--exit-when-idle")
        return subprocess.Popen(cmd, cwd=HERE, env=env)

    def emails(self):
        return SqliteMailProvider(self.provider_db).count()

    def job_states(self):
        with closing(self.queue._connect()) as db:
            return {r["kind"]: (r["state"], r["attempts"]) for r in db.execute("SELECT kind, state, attempts FROM jobs")}


@pytest.fixture
def env(tmp_path):
    return Env(tmp_path)


def wait_for(condition, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return False


def test_happy_path(env):
    assert env.client.post("/reports", json={"month": "2026-10"}).status_code == 202
    assert env.start_worker().wait(timeout=20) == 0
    assert env.report_path.read_bytes() == EXPECTED, "the report file is wrong"
    assert env.emails() == 1
    assert env.client.get("/reports/2026-10").json()["status"] == "ready"
    assert env.job_states() == {"report": ("done", 1), "report_email": ("done", 1)}


def test_requesting_a_report_twice_makes_one_job(env):
    first = env.client.post("/reports", json={"month": "2026-10"})
    second = env.client.post("/reports", json={"month": "2026-10"})
    assert first.status_code == second.status_code == 202
    assert env.queue.stats()["queued"] == 1, "a repeated request must not create a second job"
    assert env.client.post("/reports", json={"month": "2026-13"}).status_code == 422, "invalid months are refused at the door"


def test_kill_minus_nine_in_the_middle_of_the_job(env):
    env.client.post("/reports", json={"month": "2026-10"})
    victim = env.start_worker(slow=30, lease=1.5, sentinel=True)                  # the job will take 30 seconds
    assert wait_for(lambda: any(p.name.startswith("started-") for p in env.out.iterdir())), "the job never started"
    victim.send_signal(signal.SIGKILL)                                            # no cleanup, no goodbye
    victim.wait()
    assert not env.report_path.exists(), "nothing is published before the job completes"
    assert env.job_states()["report"][0] == "running", "the dead worker still 'holds' the job until its lease expires"
    assert env.start_worker(slow=0, lease=1.5).wait(timeout=30) == 0              # a new worker takes over after the lease
    assert env.report_path.read_bytes() == EXPECTED
    assert env.emails() == 1
    assert env.job_states() == {"report": ("done", 2), "report_email": ("done", 1)}


CRASH_POINTS = ["report:mid-write", "report:before-replace", "report:after-replace", "report:after-status",
                "email:after-claim", "email:after-send", "email:after-record"]


@pytest.mark.parametrize("point", CRASH_POINTS)
def test_crash_at_every_point_then_restart(env, point):
    env.client.post("/reports", json={"month": "2026-10"})
    assert env.start_worker(crash_at=point).wait(timeout=20) == 137, f"the worker was supposed to die at {point}"
    assert not env.report_path.exists() or env.report_path.read_bytes() == EXPECTED, "a reader saw a PARTIAL report"
    assert env.start_worker().wait(timeout=30) == 0
    assert env.report_path.read_bytes() == EXPECTED, "the report is wrong after recovery"
    assert env.emails() == 1, f"{env.emails()} e-mails after a crash at {point} (expected exactly one)"
    assert {s for s, _ in env.job_states().values()} == {"done"}
    assert env.client.get("/reports/2026-10").json()["status"] == "ready"


def test_sigterm_finishes_the_current_job_and_stops(env):
    env.client.post("/reports", json={"month": "2026-10"})
    env.client.post("/reports", json={"month": "2026-09"})
    worker = env.start_worker(slow=1.5, lease=20, exit_when_idle=False, sentinel=True)
    assert wait_for(lambda: any(p.name.startswith("started-") for p in env.out.iterdir()))
    worker.send_signal(signal.SIGTERM)                                            # what a deployment sends
    assert worker.wait(timeout=20) == 0, "a graceful stop exits normally"
    states = env.job_states()
    assert states["report"][0] in {"done", "queued"}
    assert (env.out / "report-2026-10.csv").exists() or (env.out / "report-2026-09.csv").exists(), "the running job was finished"
    assert env.queue.stats()["running"] == 0, "no job is left half-leased"


def test_a_poison_job_is_buried_and_others_still_run(env):
    env.queue.enqueue("report", {"month": "99-99"}, max_attempts=3)                # bypasses the API validation
    env.client.post("/reports", json={"month": "2026-10"})
    assert env.start_worker().wait(timeout=20) == 0
    stats = env.queue.stats()
    assert stats["dead"] == 1 and env.report_path.read_bytes() == EXPECTED, "the bad job must not block the good one"
```

```bash run
python -m pytest -v -p no:cacheprovider -W ignore --tb=short test_survival.py 2>&1 | grep -v "^$\|^plugins\|^hypothesis\|^rootdir\|^platform\|^collecting" | tail -20
```
```text
============================= test session starts ==============================
test_survival.py::test_happy_path PASSED                                 [  8%]
test_survival.py::test_requesting_a_report_twice_makes_one_job PASSED    [ 16%]
test_survival.py::test_kill_minus_nine_in_the_middle_of_the_job PASSED   [ 25%]
test_survival.py::test_crash_at_every_point_then_restart[report:mid-write] PASSED [ 33%]
test_survival.py::test_crash_at_every_point_then_restart[report:before-replace] PASSED [ 41%]
test_survival.py::test_crash_at_every_point_then_restart[report:after-replace] PASSED [ 50%]
test_survival.py::test_crash_at_every_point_then_restart[report:after-status] PASSED [ 58%]
test_survival.py::test_crash_at_every_point_then_restart[email:after-claim] PASSED [ 66%]
test_survival.py::test_crash_at_every_point_then_restart[email:after-send] PASSED [ 75%]
test_survival.py::test_crash_at_every_point_then_restart[email:after-record] PASSED [ 83%]
test_survival.py::test_sigterm_finishes_the_current_job_and_stops PASSED [ 91%]
test_survival.py::test_a_poison_job_is_buried_and_others_still_run PASSED [100%]
============================= 12 passed in 14.13s ==============================
```

Read the assertions: every crash test checks, **right after the death**, that a reader never sees a partial report, and **after recovery**, that the file is exactly the expected bytes, that **one** e-mail was received, and that every job is done. These are invariants, not implementation details, so the tests keep working if you change how the handlers work inside.

### 16.6 Do the tests really protect the design?

As in the earlier modules, we checked that the tests can fail. We put four plausible bugs into a copy of the project, one at a time, and ran the suite:

| The bug | Caught by |
|---|---|
| the worker acknowledges the job **before** doing the work | the `kill -9` test (the job is marked done and the report never appears) |
| the report is written to its final name directly (not atomic) | the crash test for `report:mid-write` (a reader sees a partial file) |
| the e-mail's idempotency key includes the attempt number | the crash test for `email:after-send` (two e-mails) |
| leases that never expire | the `kill -9` test (the job stays "running" for ever and the second worker never gets it) |

The second one is a good example of a bug that "works" in every normal run and in a test that only checks the final state: the retry overwrites the partial file with a complete one. Only a check made **between the crash and the recovery** can see it.

### 16.7 Run it yourself, and then extend it

> **Try it on your machine**: run the API and a worker by hand.
>
> ```bash
> # serve.py contains:  from app import create_app; app = create_app("shop.db")
> python -c "import tasks; tasks.init_db('shop.db'); tasks.seed_orders('shop.db')"
> mkdir -p out
> uvicorn serve:app &                                          # the API
> python worker_main.py --db shop.db --out out --provider-db provider.db      # a worker (Ctrl+C stops it gracefully)
> curl -s -X POST localhost:8000/reports -H 'content-type: application/json' -d '{"month": "2026-10"}'
> ```
>
> Expected reply: `{"month":"2026-10","status":"queued","status_url":"/reports/2026-10"}`. Within a second `curl localhost:8000/reports/2026-10` shows `"status":"ready"` and a digest, `out/report-2026-10.csv` exists, and `sqlite3 provider.db 'select * from messages'` shows one message. Start the worker with `SLOW_SECONDS=20`, press `kill -9 <pid>` while it works, start it again, and watch the same recovery happen after the lease (30 seconds by default).

Extensions (good practice problems):

1. **Schedule it.** Add a `Scheduler` entry (section 14) that requests last month's report at `0 2 1 * *`, with two scheduler processes running, and test that exactly one job appears.
2. **Dead-letter admin.** Add `GET /admin/jobs/dead` and `POST /admin/jobs/{id}/requeue` (protected as in swe.07) and test the redrive.
3. **Metrics.** Expose `prometheus_text(queue)` at `/metrics` and add the health alerts of section 15.
4. **Retry policy.** Make the e-mail provider fail with a temporary error 3 times and show that the report job still finishes while the e-mail job is retried with backoff.
5. **Scale out.** Run three workers at once on 50 report requests and prove every month produced exactly one file and one e-mail.
6. **Swap the engine.** Move the queue to PostgreSQL with `FOR UPDATE SKIP LOCKED`, or port the tasks to arq or Celery. The handlers (the idempotent part) should not need to change; only the enqueue and reserve code does.

## 17. Common traps

1. **Caching without a TTL**, so a missed invalidation lives for ever (5.1).
2. **Per-user data under a shared key** (4.4), and caching authorisation decisions.
3. **Deleting the cache before writing the database** (5.2); not knowing the interleavings that leave stale data.
4. **No protection against stampedes** after a restart or a popular expiry (6).
5. **Treating a cache as a database**: no plan for eviction, restarts or an empty cache (3.1, 15.5).
6. **Read-modify-write across two Redis commands** instead of an atomic one (3.2, 7.2).
7. **A lock without an expiry, or released without checking the owner**, and believing a Redis lock gives mutual exclusion (7.3).
8. **`pickle` for cached or queued data** (4.2, 10.2).
9. **Using `BackgroundTasks` for work that must not be lost** (8.3).
10. **Acknowledging before the work** (lost jobs) without having chosen at-most-once on purpose (8.4).
11. **Assuming exactly-once delivery.** Everything is at-least-once; make the work idempotent (11).
12. **A dedupe key built from the job id or the time** instead of the business fact (11.5, 11.9).
13. **Relative updates in a job** (`+= 1`), `uuid4()` or `now()` inside the handler, appending instead of upserting (11.9).
14. **Enqueueing after the commit** (or before it) instead of in the same transaction (11.7).
15. **Half-written output files** visible to readers; non-deterministic output (11.8).
16. **Leases shorter than the job, with no heartbeat**, so slow jobs run twice (9.3).
17. **Retrying permanent errors**, or retrying forever; no jitter, no cap, no breaker (12).
18. **A dead-letter queue nobody looks at**, and redriving it without idempotent handlers (12.3).
19. **Putting whole objects in payloads** (stale data, privacy); not versioning payloads across deploys (10.2).
20. **One queue for everything**, so a flood of slow jobs delays urgent ones (10.2).
21. **Schedules in a local time zone**; overlapping runs; no misfire policy; several schedulers running the same job (14).
22. **Monitoring errors but not queue age**; no alert on "work waiting, nothing completing" (15.1).
23. **Workers sized for the average load** (no headroom) or autoscaled on CPU (15.3).
24. **Unbounded queues** with no backpressure (15.4).
25. **Testing only the happy path.** Crash the worker at every line that matters, then restart it (11, 16).

## 18. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| a user sees someone else's data | a per-user answer cached under a shared key | 4.4 |
| old data stays after an update | invalidation race, no TTL, or a missed write path | 5 |
| database load spikes every N minutes | many keys expire together, or a stampede | 6 |
| `WRONGTYPE` from Redis | two features share a key name | 3.2 |
| a counter is stuck at its limit for ever | `INCR` and `EXPIRE` were separate and the process died between them | 7.2 |
| two workers run the "exclusive" job | lock expired during a pause, or released by the wrong owner | 7.3 |
| jobs vanish after a deploy | early acknowledgement, in-process background tasks | 8.3, 8.4, 13.2 |
| the customer got the e-mail twice | at-least-once delivery without idempotency | 11 |
| the same job runs twice while still running | lease shorter than the job; visibility timeout too short | 9.3, 13.2 |
| `lease-lost` outcomes in the worker log | the job was taken over; the old worker's result is ignored | 9.3 |
| a job cycles for ever / burns the provider's quota | permanent error treated as transient, no max attempts | 10.2, 12 |
| the queue grows and nothing is failing | workers stuck, too few, or blocked on a dependency | 15.1, 15.3 |
| the nightly job ran twice or not at all | several schedulers, DST, or downtime without a misfire policy | 14.3 |
| a half-empty report file on disk | writing in place instead of temp file + `os.replace` | 11.8 |
| order saved but no receipt job | enqueue outside the transaction | 11.7 |
| the whole site is down when Redis is | no fallback for cache errors | 15.5 |

## 19. Summary

- A **cache** is a copy and a **queue** is a promise. Copies go stale; promises get broken or kept twice. Design for both on purpose.
- **Caching:** measure the hit ratio; use cache-aside with a namespaced, versioned key, JSON values, a TTL with jitter, and negative caching; never cache per-user data under a shared key; accept eventual consistency and write down a staleness budget.
- **Invalidation:** change the database first, then invalidate; races leave stale data silently (a generation number in the key closes the gap); keep a TTL as the safety net.
- **Stampedes, avalanches, hot keys:** single flight, stale-while-revalidate, jitter, a small local cache in front; protect the database.
- **Redis** gives atomic commands and data structures for sessions, counters, rate limits, leaderboards and locks. Locks are an efficiency tool; correctness comes from database constraints and fencing tokens. A cache outage must degrade, not crash, the application.
- **Queues** move slow or unreliable work out of the request. Pass ids, not objects; use JSON; version payloads; separate queues by workload; answer `202` and give a status URL.
- **Delivery:** at-most-once loses jobs, at-least-once duplicates them, exactly-once delivery does not exist. Build **effectively once**: at-least-once plus idempotent work.
- **A durable queue** needs leases, an atomic claim, retries with backoff and jitter, dedupe keys, a dead-letter state and statistics. Counting attempts at reservation protects against jobs that kill workers.
- **Idempotent workers:** natural idempotency, conditional transitions, dedupe records in the same transaction, idempotency keys to the outside world, and the outbox for enqueueing. Name the key after the business fact. Test it by crashing at every window and running a second worker.
- **Reports:** deterministic content and atomic publish (`temp file`, `fsync`, `os.replace`).
- **Retries and dead letters:** classify errors, cap and jitter the delays, add a circuit breaker, alert on the dead-letter state, redrive only idempotent jobs.
- **Libraries:** Celery, RQ and arq are these ideas with more features. Read their defaults for acknowledgement timing, visibility timeout, prefetch, serialisation and retries before trusting them.
- **Schedules:** cron syntax, UTC, overlap, misfire policy; make the scheduler enqueue jobs with a dedupe key per slot so many schedulers are safe.
- **Operations:** watch queue age, depth, throughput, failures and dead letters; size workers with Little's law plus headroom; add backpressure; correlate logs with request ids; drain workers on deploy; practise killing them.

Next: the 30 problems for this module practise cache keys and invalidation interleavings, stampede and lock bugs, queue state traces with leases and retries, idempotency design and crash-window analysis, cron and time-zone reasoning, and building small workers and schedulers.
