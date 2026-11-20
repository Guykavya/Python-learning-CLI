# Why is `INCR` safe?

Chapter section 3.1 (what Redis is), 7.2 (shared rate limits) and "Try it: why is `INCR` safe?". Two web servers count page views in Redis. Server code, version 1:

```python
count = r.get("hits")               # read
r.set("hits", int(count or 0) + 1)  # modify, then write
```

Version 2:

```python
r.incr("hits")
```

In `answer.md` explain (about 150 to 250 words):

1. Give a **step-by-step timeline** with servers A and B in which version 1 loses an increment. Start from `hits = 41`.
2. Why does version 2 never lose one? Say what is special about how Redis runs **one command**.
3. Why does adding a Python `threading.Lock` around version 1 not fix it when the two servers are **separate processes on separate machines**?
4. Name the same idea in SQL and in Django (you met both in swe.03 and swe.06).
5. A rate limiter does `INCR` and then `EXPIRE` as two commands. What can still go wrong between them, and what is the one-command fix used in the chapter?

Use the words *read-modify-write*, *atomic*, *single-threaded*, *lost update*.

## Example

A good timeline line looks like: `t1  A: GET hits -> "41"`.
