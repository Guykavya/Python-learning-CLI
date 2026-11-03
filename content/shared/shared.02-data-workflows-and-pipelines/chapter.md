# Chapter 2: Data workflows and pipelines

In the last chapter you learned to ask a database questions. This chapter is about the work that happens **before** anyone can ask: getting the data into the database in the first place, again and again, every hour or every night, without losing rows, without doubling rows, and without a person watching. That work is called a **data pipeline**.

A pipeline sounds simple. "Download the orders and save them." You could write it in ten lines. The trouble is everything that happens on the second day. The API goes down halfway through. The job is started twice by mistake. One order arrives with `"amount": "N/A"`. A customer's email ends up in a log file that the whole team can read. The new version of the API adds a field and the old Parquet files no longer match. Each of these has a known, boring, reliable fix, and this chapter teaches them one at a time.

The chapter has three learning outcomes:

1. **Build a pipeline that can be re-run safely without duplicating data.** You will learn natural keys, UPSERT, "only if newer" updates and delete-and-insert per partition, and you will test the rule "run twice = same result".
2. **Resume a failed run from a checkpoint.** You will save progress atomically (a file is either the old version or the new one, never half of each), write data before the checkpoint, and reason about what happens if the program dies at each line.
3. **Quarantine bad records instead of crashing.** You will check every record against a contract, put the bad ones aside with a reason, keep going, and still stop the run when so many records are bad that something bigger must be wrong.

**A note on how examples are shown.** Every code block that has output was really run, with **Python 3.14**, **httpx 0.28.1**, **pyarrow 26.0.0** and **SQLite 3.46.1** (Linux). The output is the real output. No example touches the network: the "Pagebound Orders API" at `https://api.pagebound.test` is a fake server written in a few lines of Python with `httpx.MockTransport` (section 2). Files are written into a fresh empty folder, and paths are printed relative to it. When an example raises an exception, the traceback is shortened to its last line. Values that depend on your machine (file sizes, timings, random ids) are labelled where they appear.

You need two packages beyond the standard library: `httpx` (you met it in the concurrency chapter) and `pyarrow` (new here, for Parquet files). Both are already installed in this project. You do not need pandas, and this chapter does not use it: pyarrow and plain Python are enough, and they show more clearly what is happening.

## Table of contents

[1. What a data pipeline is](#1-what-a-data-pipeline-is) · [2. Calling an API with httpx](#2-calling-an-api-with-httpx) · [3. Pagination](#3-pagination) · [4. ETL vs ELT](#4-etl-vs-elt) · [5. Transform: flatten, parse, normalise](#5-transform-flatten-parse-normalise) · [6. Schema checks and data-quality checks](#6-schema-checks-and-data-quality-checks) · [7. Bad records and quarantine](#7-bad-records-and-quarantine) · [8. Incremental loads and watermarks](#8-incremental-loads-and-watermarks) · [9. Deduplication and idempotent writes](#9-deduplication-and-idempotent-writes) · [10. Retries](#10-retries) · [11. Checkpoints and resume](#11-checkpoints-and-resume) · [12. Logging and run summaries](#12-logging-and-run-summaries) · [13. Files: CSV vs Parquet](#13-files-csv-vs-parquet) · [14. Partitioning](#14-partitioning) · [15. Schema evolution](#15-schema-evolution) · [16. Sensitive data](#16-sensitive-data) · [17. Putting it together](#17-putting-it-together) · [18. Testing pipelines](#18-testing-pipelines) · [19. Module project preview](#19-module-project-preview) · [20. Summary](#20-summary)

## 1. What a data pipeline is

### 1.1 The problem pipelines solve

Pagebound, the bookshop from the last chapter, has grown. Orders are no longer typed into SQLite by hand. They are taken by an **order service**, a separate program run by another team, which offers an **API**: a web address you can ask, "give me the orders", and it answers with JSON.

Three groups of people want those orders somewhere else:

- **Finance** wants a SQLite database with one row per order, so they can write the `GROUP BY` queries you learned last chapter. They want it updated every hour.
- **Analysts** want files they can open in any tool, one folder per day, so they can study a year of orders without asking the order service for a year of data each time.
- **Support** wants to look up an order by its id, but they must not see customers' email addresses.

None of these people should call the order service directly. It is busy taking orders; it was not built for analysis; and it only keeps recent data. So somebody writes a program that **copies** the data from where it is made to where it is used, and runs that program on a schedule. That program is a data pipeline.

### 1.2 The parts of a pipeline

Every pipeline, however large, has the same five parts:

```text
 source  --->  extract  --->  transform  --->  load  --->  sink
 (API)        (fetch)        (clean, check)    (write)    (SQLite, Parquet)
```

- **Source**: where the data lives now. Here, the order service API. Other sources are files dropped in a folder, another database, or a message queue.
- **Extract**: read the data out of the source. For an API this means HTTP requests, pages, retries and timeouts (sections 2, 3 and 10).
- **Transform**: turn the raw data into the shape you want. Flatten nested JSON, turn the text `"19.99"` into a money value, turn `"2024-06-01T10:00:00Z"` into a real date and time, check that every record follows the rules, set bad records aside (sections 5, 6 and 7).
- **Load**: write the result into the destination, in a way that is safe to repeat (sections 8, 9 and 11).
- **Sink**: the destination. Here, a SQLite database and a folder of Parquet files (sections 13 and 14).

Around these five parts sit the things that make a pipeline trustworthy: **state** (what did the last run get to?), **logging** (what happened?), and **rules about sensitive data** (who may see what?).

### 1.3 Batch and streaming

There are two broad ways to move data.

- **Batch**: the pipeline runs now and then (every hour, every night), takes everything that changed since last time, processes it as a group, and stops. Most business reporting works like this.
- **Streaming**: the pipeline runs all the time and handles each event within seconds of it happening. Fraud detection and live dashboards work like this.

Between them is **micro-batch**: a batch job that runs every minute. The ideas in this chapter (watermarks, idempotent writes, checkpoints, quarantine) apply to all three, but the code is batch code, because batch is what you will write first in almost every job, and it is easier to see and test.

### 1.4 What "good" means

A pipeline that works once is easy. A good pipeline keeps working on bad days. Four properties describe "good":

| Property | Question it answers | What breaks without it |
|---|---|---|
| **Correct** | Is every value right, and is every record there exactly once? | Revenue reports are wrong and nobody knows. |
| **Re-runnable** (idempotent) | If I run it again with the same input, do I get the same result? | Running the job twice doubles the data. |
| **Resumable** | If it dies halfway, can it continue from where it stopped? | A crash at page 900 of 1,000 means starting again from page 1. |
| **Observable** | Can I tell what it did, how much, how long, and what went wrong? | You learn about problems from an angry analyst, days later. |

A fifth property is about people, not data: the pipeline must be **safe**. It must not leak personal data or secrets into places where they do not belong (section 16).

The word **idempotent** will appear often. An operation is idempotent if doing it twice has the same effect as doing it once. "Set the light to on" is idempotent: press it twice and the light is still on. "Toggle the light" is not. "Add this order to the table" is not idempotent; "make sure this order is in the table with these values" is. Much of this chapter is about turning the first kind of write into the second kind.

### 1.5 A tiny pipeline, and its first bug

Here is a pipeline in its smallest form. The source is a Python list, the sink is a SQLite table.

```python
import sqlite3

source = [
    {"id": 1, "amount": 10},
    {"id": 2, "amount": 20},
    {"id": 3, "amount": 30},
]

def naive_pipeline(con):
    con.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER, amount INTEGER)")
    for row in source:                                   # extract (trivial here)
        con.execute("INSERT INTO orders VALUES (?, ?)",  # load
                    (row["id"], row["amount"]))
    con.commit()

con = sqlite3.connect(":memory:")
naive_pipeline(con)
print("after run 1:", con.execute("SELECT COUNT(*), SUM(amount) FROM orders").fetchone())
naive_pipeline(con)
print("after run 2:", con.execute("SELECT COUNT(*), SUM(amount) FROM orders").fetchone())
```
```text
after run 1: (3, 60)
after run 2: (6, 120)
```

The first run is fine. The second run, which might happen because a scheduler retried, or because someone pressed "run" to be sure, **doubled** the data. Finance now sees revenue of 120 instead of 60. Nothing crashed, no error was printed, and the numbers are wrong. This is the most common pipeline bug in the world.

The fix is to say what makes a row unique (the order `id`) and to write "insert, or update if it is already there", the UPSERT from the last chapter:

```python
def safe_pipeline(con):
    con.execute("CREATE TABLE IF NOT EXISTS orders2 (id INTEGER PRIMARY KEY, amount INTEGER)")
    with con:                                            # one transaction
        for row in source:
            con.execute(
                "INSERT INTO orders2 (id, amount) VALUES (?, ?) "
                "ON CONFLICT(id) DO UPDATE SET amount = excluded.amount",
                (row["id"], row["amount"]),
            )

safe_pipeline(con)
safe_pipeline(con)
safe_pipeline(con)
print("after 3 runs:", con.execute("SELECT COUNT(*), SUM(amount) FROM orders2").fetchone())
```
```text
after 3 runs: (3, 60)
```

Three runs, same answer. That is the whole idea of idempotency in one example. The rest of the chapter is about keeping that property when the source is a slow, paged, sometimes-failing API, when the data changes between runs, and when the program can die at any line.

### 1.6 Try it: pipeline basics

**Try it 1.** For each line of `naive_pipeline`, name the pipeline part it belongs to: source, extract, transform, load, or sink. Is there a transform step at all?

<details><summary>Answer</summary>

- `source` (the list) is the **source**.
- `for row in source:` is the **extract** (reading records out of the source). With an API it would be HTTP calls.
- `con.execute("INSERT ...")` and `con.commit()` are the **load**.
- The `orders` table in SQLite is the **sink**.
- There is **no transform**: the values are written exactly as they arrive. Real data almost always needs one (types, flattening, checks), which is section 5.

</details>

**Try it 2.** Suppose `naive_pipeline` crashes with an exception after inserting row 2 but before `con.commit()`. The program exits. What is in the table afterwards, and what happens when you run it again? (Remember from the last chapter what happens to an uncommitted transaction.)

<details><summary>Answer</summary>

Python's `sqlite3` opens a transaction before the first `INSERT`, and nothing is saved until `commit()`. If the program dies before the commit, the transaction is rolled back, so the table is **empty** (or holds only what earlier, committed runs wrote). Running again inserts rows 1 to 3 once, which is correct this time. So the naive pipeline is accidentally safe against this crash, because of the transaction, and unsafe against a plain second run, because of the missing key. Sections 9 and 11 make both cases safe on purpose.

</details>

**Try it 3.** Which of these operations are idempotent? (a) `UPDATE orders SET status = 'shipped' WHERE id = 7`; (b) `UPDATE accounts SET balance = balance + 100 WHERE id = 7`; (c) `DELETE FROM orders WHERE order_date = '2024-06-01'`; (d) appending a line to a log file.

<details><summary>Answer</summary>

(a) **Idempotent**: after one or ten runs, order 7 is shipped. (b) **Not idempotent**: each run adds another 100. (c) **Idempotent**: once the rows are gone, deleting again changes nothing. (d) **Not idempotent**: each run adds another line. A useful test: "if I do it twice, is the world different from doing it once?"

</details>

## 2. Calling an API with httpx

### 2.1 What an HTTP API is, in one page

An HTTP API is a program that listens at a web address and answers **requests** with **responses**. You met this in the concurrency chapter; here is what matters for pipelines.

A **request** has:

- a **method**: `GET` to read, `POST` to create, `PUT`/`PATCH` to change, `DELETE` to remove. Pipelines mostly `GET`.
- a **URL**: `https://api.pagebound.test/v1/orders?page=2&per_page=3`. The part after `?` is the **query string**, made of **parameters** (`page=2`, `per_page=3`).
- **headers**: extra information such as `Authorization: Bearer <token>` (who you are) or `Accept: application/json`.

A **response** has:

- a **status code**, a three-digit number that says how it went;
- **headers**, such as `Content-Type: application/json` or `Retry-After: 30`;
- a **body**, which for most data APIs is JSON text.

Status codes come in families. You should know these by heart, because the pipeline's behaviour depends on them:

| Code | Name | What the pipeline should do |
|---|---|---|
| 200 | OK | Use the body. |
| 400 | Bad Request | Your request is wrong. Fix the code; retrying will not help. |
| 401 / 403 | Unauthorized / Forbidden | Bad or missing credentials. Stop and tell a human. |
| 404 | Not Found | Wrong URL (or the thing is gone). Do not retry. |
| 429 | Too Many Requests | You are going too fast. Wait (often the `Retry-After` header says how long) and retry. |
| 500, 502, 503, 504 | Server errors | The server had a problem. Usually temporary: wait and retry. |

The rule of thumb: **4xx means "you did something wrong", 5xx means "the server did"**, and 429 is the one 4xx that means "wait".

### 2.2 Running offline: `httpx.MockTransport`

Real APIs need a network, an account, and a server that is up. That is bad for learning and terrible for tests: a test that fails because the Wi-Fi dropped teaches nothing. httpx has a clean answer. A `Client` sends requests through a **transport**; the normal transport opens network connections. `httpx.MockTransport(handler)` is a transport that, instead, calls a Python function you write. Your function gets the `httpx.Request` and returns an `httpx.Response`. No network is used at all.

```python
import httpx

def handler(request: httpx.Request) -> httpx.Response:
    print("server saw:", request.method, request.url)
    return httpx.Response(200, json={"hello": "pipeline"})

client = httpx.Client(transport=httpx.MockTransport(handler))
response = client.get("https://api.pagebound.test/ping")
print(response.status_code, response.json())
```
```text
server saw: GET https://api.pagebound.test/ping
200 {'hello': 'pipeline'}
```

Everything on the client side (`client.get`, `response.json()`, `raise_for_status()`, headers, parameters) behaves exactly as it would against a real server. That is why the same pipeline code can run against the fake server in tests and the real server in production: only the transport changes.

The handler can do anything a server does: look at the path and parameters, return different status codes, add headers, or even **raise** a network error such as `httpx.ConnectError` to pretend the network failed. You will use all of these.

### 2.3 `httpx.Client`: base URL, parameters, headers

You can call `httpx.get(url)` directly, but a pipeline should use one `httpx.Client` for the whole run, for three reasons:

1. **Connection reuse.** A client keeps connections open between requests, so page 2 does not pay to set up a new connection. Over a thousand pages this matters a lot.
2. **Shared settings.** The base URL, timeouts and headers (such as the API token) are set once.
3. **Testability.** Functions that take a `client` argument can be given a client with a mock transport in tests. Functions that call `httpx.get` themselves cannot.

```python
client = httpx.Client(
    transport=httpx.MockTransport(handler),
    base_url="https://api.pagebound.test",
    headers={"Accept": "application/json"},
)
response = client.get("/v1/orders", params={"page": 2, "per_page": 3, "status": "shipped"})
print(response.request.url)
print(response.request.headers["accept"])
```
```text
server saw: GET https://api.pagebound.test/v1/orders?page=2&per_page=3&status=shipped
https://api.pagebound.test/v1/orders?page=2&per_page=3&status=shipped
application/json
```

Notice three things. The path `/v1/orders` was joined onto `base_url`. The `params` dictionary was turned into a query string, with the numbers converted to text and everything properly escaped; never build query strings by gluing strings together. And the header was sent on the request without you repeating it.

Use the client as a context manager so its connections are closed when you are done:

```python
with httpx.Client(base_url="https://api.pagebound.test", timeout=10.0) as client:
    ...   # all requests for this run
```

### 2.4 Status codes and `raise_for_status()`

httpx does **not** raise an exception for a 404 or a 500. The response comes back normally, with `status_code` set. If you forget to check, your pipeline will happily try to read the body of an error page as data. The method `response.raise_for_status()` raises `httpx.HTTPStatusError` for any 4xx or 5xx code, and does nothing for 2xx.

```python
import httpx

def handler(request):
    if request.url.path == "/v1/orders":
        return httpx.Response(200, json={"data": []})
    return httpx.Response(404, json={"error": "no such endpoint"})

client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.pagebound.test")

ok = client.get("/v1/orders")
print(ok.status_code, ok.is_success, ok.raise_for_status() is ok)

bad = client.get("/v1/ordrs")                  # a typo in the path
print(bad.status_code, bad.is_success)
try:
    bad.raise_for_status()
except httpx.HTTPStatusError as error:
    print(type(error).__name__, error.response.status_code)
    print(str(error).splitlines()[0])
```
```text
200 True True
404 False
HTTPStatusError 404
Client error '404 Not Found' for url 'https://api.pagebound.test/v1/ordrs'
```

(`raise_for_status()` returns the response itself when it succeeds, which is why the first line printed `True` at the end; this lets you write `client.get(...).raise_for_status().json()` in one line.)

The exception carries the response, so `error.response.status_code` tells you which code it was. That is what the retry logic in section 10 looks at.

There is a second family of errors: the ones where there is **no response at all**. The connection was refused, the name did not resolve, the server took too long. httpx raises subclasses of `httpx.TransportError` for these: `httpx.ConnectError`, `httpx.ReadTimeout`, `httpx.ConnectTimeout`, and others. Both families share the base class `httpx.HTTPError`.

```text
httpx.HTTPError
├── httpx.HTTPStatusError     a response came back with 4xx or 5xx (after raise_for_status)
└── httpx.TransportError      no usable response
    ├── httpx.TimeoutException   (ConnectTimeout, ReadTimeout, WriteTimeout, PoolTimeout)
    └── httpx.NetworkError       (ConnectError, ReadError, ...)
```

### 2.5 JSON bodies, and bodies that are not JSON

`response.json()` parses the body as JSON and returns Python objects: dicts, lists, strings, numbers, `True`/`False`/`None`. But a server under stress sometimes answers `200 OK` with an HTML error page from a proxy, or with an empty body. Then `.json()` raises `json.JSONDecodeError`, a subclass of `ValueError`, with a message that says nothing about which URL failed.

```python
def html_handler(request):
    return httpx.Response(200, text="<html><body>Gateway busy</body></html>",
                          headers={"Content-Type": "text/html"})

client = httpx.Client(transport=httpx.MockTransport(html_handler), base_url="https://api.pagebound.test")
response = client.get("/v1/orders")
print(response.headers["content-type"])
response.json()
```
```text
text/html
Traceback (most recent call last):
  ...
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

"Expecting value: line 1 column 1" is a confusing message at three in the morning. A small helper turns it into an error that names the URL and shows the start of the body. It is worth writing once and using everywhere:

```python
import json

class BadResponse(Exception):
    """The server answered, but not with the JSON we expected."""

def get_json(client, path, params=None):
    response = client.get(path, params=params)
    response.raise_for_status()
    if response.status_code == 204:            # 204 No Content: success, but there is no body
        return None
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        start = response.text[:60]
        raise BadResponse(f"GET {response.request.url} returned non-JSON body: {start!r}") from exc

try:
    get_json(client, "/v1/orders", params={"page": 1})
except BadResponse as error:
    print(error)
    print("caused by:", type(error.__cause__).__name__, "-", error.__cause__)
```
```text
GET https://api.pagebound.test/v1/orders?page=1 returned non-JSON body: '<html><body>Gateway busy</body></html>'
caused by: JSONDecodeError - Expecting value: line 1 column 1 (char 0)
```

`raise NewError(...) from exc` **chains** the exceptions: the new error carries the original one in its `__cause__` attribute, and a traceback shows both, joined by the line "The above exception was the direct cause of the following exception". That is usually what you want: your message says what went wrong in pipeline terms (which URL, what the body looked like), and the original says exactly where the parser gave up. If the original adds nothing, `raise NewError(...) from None` hides it instead. What you should **not** do is let the bare `JSONDecodeError` escape, or catch it and raise a new error without `from`, which still shows both but with the misleading line "During handling of the above exception, another exception occurred", as if your error handler itself had crashed.

**A success with no body.** Status 204 means "No Content": the request worked and the server deliberately sent nothing back. Some APIs answer 204 for "nothing to report", for example an export endpoint with no new data. `raise_for_status()` is happy (204 is a 2xx code), but `.json()` fails, because an empty body is not valid JSON:

```python
def no_content_handler(request):
    return httpx.Response(204)

client = httpx.Client(transport=httpx.MockTransport(no_content_handler), base_url="https://api.pagebound.test")
response = client.get("/v1/exports/latest")
print(response.status_code, response.is_success, repr(response.content))
print("get_json returns:", get_json(client, "/v1/exports/latest"))
response.json()
```
```text
204 True b''
get_json returns: None
Traceback (most recent call last):
  ...
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

That is why `get_json` checks for 204 **before** parsing and returns `None`. The caller must then decide what "no content" means for it (usually: nothing to do this time).

### 2.6 Timeouts

A request with no timeout can wait **forever** if the server accepts the connection and then never answers. Your nightly job is then still "running" the next morning, holding a lock, and nothing is logged. Always have a timeout. httpx gives every client a default of 5 seconds, and you can set your own:

```python
client = httpx.Client(base_url="https://api.pagebound.test", timeout=10.0)
# or finer control: 5 s to connect, 30 s to read a slow page
client = httpx.Client(base_url="https://api.pagebound.test",
                      timeout=httpx.Timeout(30.0, connect=5.0))
```

You should **never** pass `timeout=None` in a pipeline. When a timeout fires, httpx raises `httpx.ReadTimeout` (or `ConnectTimeout`), which is a `TransportError` and therefore something you may retry (section 10). A mock handler can raise it to test that path without waiting for anything:

```python
def slow_handler(request):
    raise httpx.ReadTimeout("server took too long (simulated)", request=request)

client = httpx.Client(transport=httpx.MockTransport(slow_handler), base_url="https://api.pagebound.test")
try:
    client.get("/v1/orders")
except httpx.TransportError as error:
    print(type(error).__name__, "|", error, "| is a TimeoutException:", isinstance(error, httpx.TimeoutException))
```
```text
ReadTimeout | server took too long (simulated) | is a TimeoutException: True
```

### 2.7 The fake Pagebound Orders API

From now on, most examples use one fake server. Here it is in full. Read it once carefully: it is a tiny but honest model of a real orders API, and knowing exactly what it does makes every later example easy to follow.

Each order looks like the record below. Note the details that make real data awkward: `amount` is a **string** (APIs often send money as text so it is not rounded by a float), `city` may be `null`, `status` is one of `shipped`, `pending` or `cancelled`, times are ISO 8601 text in UTC (the `Z` means UTC), and the line items are a nested list.

```python
import httpx

ORDERS = [
    {"id": 101, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
     "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
     "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]},
    {"id": 102, "customer": {"email": "ben@example.com", "city": None}, "status": "pending",
     "amount": "5.50", "currency": "INR", "created_at": "2024-06-01T11:30:00Z",
     "updated_at": "2024-06-01T12:30:00Z", "items": [{"sku": "B2", "qty": 1}]},
    {"id": 103, "customer": {"email": "chen@example.com", "city": "Delhi"}, "status": "shipped",
     "amount": "42.00", "currency": "INR", "created_at": "2024-06-02T09:15:00Z",
     "updated_at": "2024-06-02T09:15:00Z", "items": [{"sku": "B1", "qty": 1}, {"sku": "B3", "qty": 3}]},
    {"id": 104, "customer": {"email": "dia@example.com", "city": "Mumbai"}, "status": "cancelled",
     "amount": "12.25", "currency": "INR", "created_at": "2024-06-02T14:00:00Z",
     "updated_at": "2024-06-03T08:00:00Z", "items": [{"sku": "B4", "qty": 1}]},
    {"id": 105, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
     "amount": "7.75", "currency": "INR", "created_at": "2024-06-03T10:00:00Z",
     "updated_at": "2024-06-03T10:00:00Z", "items": [{"sku": "B2", "qty": 2}]},
    {"id": 106, "customer": {"email": "eli@example.com", "city": "Chennai"}, "status": "pending",
     "amount": "30.00", "currency": "INR", "created_at": "2024-06-03T16:45:00Z",
     "updated_at": "2024-06-03T16:45:00Z", "items": [{"sku": "B5", "qty": 1}, {"sku": "B1", "qty": 1}]},
    {"id": 107, "customer": {"email": "farah@example.com", "city": "Pune"}, "status": "shipped",
     "amount": "15.00", "currency": "INR", "created_at": "2024-06-04T08:20:00Z",
     "updated_at": "2024-06-04T09:00:00Z", "items": [{"sku": "B3", "qty": 1}]},
]

def make_handler(orders, log=None, inclusive=False):
    """A fake GET /v1/orders. Sorted by (updated_at, id). Page-number pagination.

    updated_since=T returns orders with updated_at > T (or >= T when inclusive=True).
    Every request's parameters are appended to `log`, so we can see what was asked.
    """
    def handler(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if log is not None:
            log.append(dict(params))
        if request.url.path != "/v1/orders":
            return httpx.Response(404, json={"error": "no such endpoint"})
        rows = sorted(orders, key=lambda o: (o["updated_at"], o["id"]))
        since = params.get("updated_since")
        if since is not None:
            if inclusive:
                rows = [o for o in rows if o["updated_at"] >= since]
            else:
                rows = [o for o in rows if o["updated_at"] > since]
        page = int(params.get("page", "1"))
        per_page = int(params.get("per_page", "3"))
        start = (page - 1) * per_page
        chunk = rows[start:start + per_page]
        next_page = page + 1 if start + per_page < len(rows) else None
        return httpx.Response(200, json={"data": chunk, "page": page, "next_page": next_page})
    return handler

def make_client(orders=ORDERS, log=None, inclusive=False):
    transport = httpx.MockTransport(make_handler(orders, log, inclusive))
    return httpx.Client(transport=transport, base_url="https://api.pagebound.test")
```

The contract, in words, as an API's documentation would state it:

- `GET /v1/orders?page=N&per_page=K` returns `{"data": [...up to K orders...], "page": N, "next_page": N+1 or null}`. Pages start at 1. Default `per_page` is 3.
- Orders come sorted by `updated_at`, then `id` (oldest change first).
- `updated_since=T` returns only orders changed **after** `T` (strictly later). Section 8 also uses the `>=` version.

(The fake server compares the timestamps as text. That works only because every timestamp here has exactly the same format; a real server parses them. Section 5 shows how you should handle them on the client side.)

Let us ask it for the first page:

```python
log = []
client = make_client(log=log)
body = client.get("/v1/orders", params={"page": 1, "per_page": 3}).raise_for_status().json()
print(sorted(body))
print([order["id"] for order in body["data"]], "next_page =", body["next_page"])
print(body["data"][0]["amount"], type(body["data"][0]["amount"]).__name__)
print("requests made:", log)
```
```text
['data', 'next_page', 'page']
[101, 102, 103] next_page = 2
19.99 str
requests made: [{'page': '1', 'per_page': '3'}]
```

The parameter values in `log` are strings (`'1'`, `'3'`), because a query string is text. The server had to turn them back into numbers with `int(...)`.

### 2.8 Try it: HTTP and httpx

**Try it 4.** What URL does this request go to? Write it out in full, then check by running it against a mock handler that prints `request.url`.

```python
client = httpx.Client(base_url="https://api.pagebound.test/v1")
client.get("/orders", params={"status": "shipped", "q": "salt & stars"})
```

<details><summary>Answer</summary>

```python
import httpx

def handler(request):
    print(request.url)
    return httpx.Response(200, json={})

client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.pagebound.test/v1")
client.get("/orders", params={"status": "shipped", "q": "salt & stars"})
```
```text
https://api.pagebound.test/v1/orders?status=shipped&q=salt+%26+stars
```

The path is appended to the base URL's path (`/v1` + `/orders`). The space becomes `+` and the `&` inside the value becomes `%26`, so it is not mistaken for the start of the next parameter. This escaping is why you pass `params=` instead of building the string yourself.

</details>

**Try it 5.** The fake API is asked for `/v1/orders?page=9`. Seven orders exist and `per_page` is 3. What status code and body come back? Is it an error?

<details><summary>Answer</summary>

```python
print(client.get("/v1/orders", params={"page": 9}).json())
```
```text
{'data': [], 'page': 9, 'next_page': None}
```

Status 200 with an empty `data` list and `next_page` null. Asking for a page past the end is **not** an error for this API; it is simply empty. Other APIs return 404 or 400 for this. You must read each API's contract, and section 3.6 shows why your stop rule should not depend on guessing.

</details>

**Try it 6.** Your colleague writes:

```python
try:
    data = client.get("/v1/orders").json()
except httpx.HTTPStatusError:
    log.warning("API error, skipping")
```

The server returns 503 with the body `{"error": "maintenance"}`. What happens? What is the fix?

<details><summary>Answer</summary>

Nothing raises. httpx does not raise for 503 by itself, and the body is valid JSON, so `data` becomes `{"error": "maintenance"}` and the pipeline carries on with an error message as if it were data, probably crashing later with a confusing `KeyError: 'data'`. The `except` never runs. The fix is to call `raise_for_status()` before `.json()` (or use a helper like `get_json` from section 2.5), so the 503 becomes an `HTTPStatusError` right where it happened.

</details>

## 3. Pagination

### 3.1 Why APIs split results into pages

An API that has a million orders will not send them in one response. That answer would be hundreds of megabytes, take minutes, use huge memory on both sides, and fail completely if the connection dropped at 99 percent. So APIs return results in **pages**: a limited number of records per response, plus some way to ask for the next page.

There are three common styles. You must recognise all three, because each needs a slightly different loop:

| Style | You send | The response tells you | Example |
|---|---|---|---|
| **Page number** | `page=2&per_page=100` | the next page number, or a total count | `{"data": [...], "next_page": 3}` |
| **Offset/limit** | `offset=200&limit=100` | sometimes a total | `{"data": [...], "total": 1234}` |
| **Cursor** | `cursor=eyJhZnRlciI6MTA1fQ` | an opaque "next" token | `{"items": [...], "next_cursor": "..."}` |
| **Link / next URL** | nothing; follow the URL given | a full URL for the next page, in a header or the body | `Link: <https://...&page=3>; rel="next"` |

(Link/next URL is really a way of delivering one of the other styles: the server builds the next URL for you.)

### 3.2 Page-number pagination

The loop is: ask for page 1; take its data; if `next_page` is set, ask for that page; stop when it is `null`.

```python
def fetch_all_pages(client, per_page=3):
    records = []
    page = 1
    while page is not None:
        body = client.get("/v1/orders", params={"page": page, "per_page": per_page}).raise_for_status().json()
        records.extend(body["data"])
        page = body["next_page"]
    return records

log = []
orders = fetch_all_pages(make_client(log=log))
print(len(orders), [o["id"] for o in orders])
print("pages requested:", [entry["page"] for entry in log])
```
```text
7 [101, 102, 103, 104, 105, 106, 107]
pages requested: ['1', '2', '3']
```

Three requests for seven orders: pages of 3, 3 and 1. The loop variable `page` is driven by what the **server** says (`next_page`), not by the client's own counting. That matters: the server knows when the data ends; the client is only guessing.

With `per_page=10` the same loop makes one request:

```python
log.clear()
print(len(fetch_all_pages(make_client(log=log), per_page=10)), "orders in", len(log), "request")
```
```text
7 orders in 1 request
```

**Choosing a page size.** Bigger pages mean fewer requests (less overhead, fewer chances to hit a rate limit) but bigger responses (more memory, more to redo if one page fails). APIs usually set a maximum (often 100 or 1,000). Take the largest page the API allows unless pages become huge.

### 3.3 Offset/limit pagination

Offset/limit is page numbering in different units: "skip the first 200 records, give me the next 100". Page `p` with size `n` is `offset = (p - 1) * n`. Some offset APIs tell you the total count; others do not, and you stop when a page comes back **empty**.

```python
import httpx

def offset_handler(request):
    offset = int(request.url.params.get("offset", "0"))
    limit = int(request.url.params.get("limit", "3"))
    rows = sorted(ORDERS, key=lambda o: o["id"])[offset:offset + limit]
    return httpx.Response(200, json={"data": rows})

def fetch_all_offset(client, limit=3):
    records, offset, calls = [], 0, 0
    while True:
        body = client.get("/v1/orders", params={"offset": offset, "limit": limit}).raise_for_status().json()
        calls += 1
        if not body["data"]:          # an empty page means we are past the end
            break
        records.extend(body["data"])
        offset += len(body["data"])
    return records, calls

client = httpx.Client(transport=httpx.MockTransport(offset_handler), base_url="https://api.pagebound.test")
records, calls = fetch_all_offset(client)
print(len(records), "records,", calls, "calls")
```
```text
7 records, 4 calls
```

Four calls for seven records: the fourth call returned an empty page, which is how the loop knew to stop. That extra call is the price of an API that does not tell you when it is done.

Notice `offset += len(body["data"])` rather than `offset += limit`. If the server ever returns fewer records than you asked for (some cap the limit silently), adding `limit` would skip records. Adding what you actually received never does.

### 3.4 Cursor pagination

With a **cursor**, the server hands you a token that means "continue from here". You do not know what is inside it and must not try to build one yourself; you send back exactly what you were given. It is **opaque**.

Behind the scenes a cursor usually encodes the last key seen, such as "after id 105". The server then answers with `WHERE id > 105 ORDER BY id LIMIT 3`. This is called **keyset** pagination, and it is faster and safer than offsets for reasons you will see in section 3.8. Our fake cursor API encodes the last id inside base64 text, just to make it look opaque:

```python
import base64
import json
import httpx

def encode_cursor(last_id):
    return base64.urlsafe_b64encode(json.dumps({"after": last_id}).encode()).decode()

def decode_cursor(cursor):
    return json.loads(base64.urlsafe_b64decode(cursor))["after"]

def make_cursor_handler(orders, log):
    def handler(request):
        params = request.url.params
        log.append(dict(params))
        limit = int(params.get("limit", "3"))
        after = decode_cursor(params["cursor"]) if "cursor" in params else 0
        rows = [o for o in sorted(orders, key=lambda o: o["id"]) if o["id"] > after]
        chunk = rows[:limit]
        next_cursor = encode_cursor(chunk[-1]["id"]) if len(rows) > limit else None
        return httpx.Response(200, json={"items": chunk, "next_cursor": next_cursor})
    return handler

def fetch_all_cursor(client, limit=3):
    records = []
    params = {"limit": limit}                 # the first call has no cursor
    while True:
        body = client.get("/v1/orders", params=params).raise_for_status().json()
        records.extend(body["items"])
        if body["next_cursor"] is None:
            return records
        params = {"limit": limit, "cursor": body["next_cursor"]}

log = []
client = httpx.Client(transport=httpx.MockTransport(make_cursor_handler(ORDERS, log)),
                      base_url="https://api.pagebound.test")
records = fetch_all_cursor(client)
print([o["id"] for o in records])
for entry in log:
    print(entry)
```
```text
[101, 102, 103, 104, 105, 106, 107]
{'limit': '3'}
{'limit': '3', 'cursor': 'eyJhZnRlciI6IDEwM30='}
{'limit': '3', 'cursor': 'eyJhZnRlciI6IDEwNn0='}
```

The cursor `eyJhZnRlciI6IDEwM30=` looks like noise; it is base64 for `{"after": 103}`. Your code never looks inside. If the API team changes the cursor format next month, your pipeline keeps working, because it only passes the token back.

One more important property: a cursor is **the natural checkpoint**. If your pipeline saves "the cursor for the next page" after each page, it can resume from exactly there after a crash. Section 11 builds that.

### 3.5 Link headers and next URLs

Some APIs (GitHub's is the famous example) put the next page's full URL in a `Link` response header:

```text
Link: <https://api.pagebound.test/v1/orders?page=2&per_page=3>; rel="next"
```

Others put it in the body, as `"next": "https://..."`. Either way the loop is: request a URL; read the next URL; stop when there is none. httpx parses the `Link` header for you into `response.links`, a dictionary keyed by `rel`:

```python
import httpx

def link_handler(request):
    page = int(request.url.params.get("page", "1"))
    rows = ORDERS[(page - 1) * 3: page * 3]
    headers = {}
    if page * 3 < len(ORDERS):
        headers["Link"] = f'<https://api.pagebound.test/v1/orders?page={page + 1}&per_page=3>; rel="next"'
    return httpx.Response(200, json=rows, headers=headers)

client = httpx.Client(transport=httpx.MockTransport(link_handler), base_url="https://api.pagebound.test")
first = client.get("/v1/orders", params={"per_page": 3})
print(first.headers["link"])
print(first.links)
```
```text
<https://api.pagebound.test/v1/orders?page=2&per_page=3>; rel="next"
{'next': {'url': 'https://api.pagebound.test/v1/orders?page=2&per_page=3', 'rel': 'next'}}
```

```python
def fetch_by_links(client, first_url, max_pages=100):
    url, records, pages = first_url, [], 0
    while url is not None:
        if pages == max_pages:
            raise RuntimeError(f"still a next link after {max_pages} pages: {url}")
        response = client.get(url).raise_for_status()
        records.extend(response.json())
        pages += 1
        url = response.links.get("next", {}).get("url")   # None when there is no next link
    return records, pages

records, pages = fetch_by_links(client, "/v1/orders?per_page=3")
print(len(records), "records in", pages, "pages")
try:
    fetch_by_links(client, "/v1/orders?per_page=3", max_pages=2)
except RuntimeError as error:
    print(error)
```
```text
7 records in 3 pages
still a next link after 2 pages: https://api.pagebound.test/v1/orders?page=3&per_page=3
```

`response.links.get("next", {}).get("url")` reads "the URL of the `next` link, or `None` if there is no such link": the first `.get` returns an empty dict when the header has no `next`, and the second `.get` on an empty dict returns `None`, which ends the loop. The `max_pages` guard works exactly as in section 3.7 below: a next-URL API can loop for ever just as easily as a page-number one, so every pagination loop gets a limit.

Passing a full URL such as `https://api.pagebound.test/v1/orders?page=2&per_page=3` to a client with a `base_url` works: an absolute URL is used as it is. Do not add your own `params=` when following a next URL; the URL already contains everything the server wants, and adding parameters again can duplicate or override them.

**A safety question about next URLs.** Should your pipeline follow a next URL that points to a different host? Usually not. If a bug or an attacker makes the API return `https://evil.test/...`, your client would send its `Authorization` header there. A careful pipeline checks that the next URL's host matches the base URL's host before following it.

### 3.6 Stopping rules

Every pagination loop needs a rule for when to stop, and wrong stop rules are a classic source of silent data loss. The safe rules, in order of preference:

1. **The server says there is no next page**: `next_page` is null, `next_cursor` is null, no `rel="next"` link. This is the best signal because it comes from the side that knows.
2. **An empty page**: when the API gives no explicit signal (offset APIs, section 3.3). It costs one extra request.
3. **A total count**: if the API says `"total": 1234`, you can stop after 1,234 records. But totals can change while you page, so prefer rule 1 or 2 if the API offers them.

And the rule that looks clever but is dangerous:

- **"Stop when a page is shorter than `per_page`."** This saves the extra request, but it is only correct if the API promises that every page except the last is full. Many APIs do not. Some filter records **after** fetching a page (for example, removing records you are not allowed to see), so page 2 of 5 might contain 97 records out of 100, and a "short page" rule would stop there and silently lose pages 3 to 5. Only use it when the documentation guarantees full pages.

Here is a loop with a short-page rule against an API whose pages are not always full. The API removes cancelled orders from each page after slicing it, which is a realistic thing for a permission or status filter to do:

```python
import httpx

def filtered_handler(request):
    page = int(request.url.params.get("page", "1"))
    chunk = ORDERS[(page - 1) * 3: page * 3]
    visible = [o for o in chunk if o["status"] != "cancelled"]      # filtered after slicing
    next_page = page + 1 if page * 3 < len(ORDERS) else None
    return httpx.Response(200, json={"data": visible, "next_page": next_page})

client = httpx.Client(transport=httpx.MockTransport(filtered_handler), base_url="https://api.pagebound.test")

def fetch_short_page_rule(client, per_page=3):
    records, page = [], 1
    while True:
        data = client.get("/v1/orders", params={"page": page}).raise_for_status().json()["data"]
        records.extend(data)
        if len(data) < per_page:          # "a short page must be the last one" (wrong here)
            return records
        page += 1

def fetch_next_page_rule(client):
    records, page = [], 1
    while page is not None:
        body = client.get("/v1/orders", params={"page": page}).raise_for_status().json()
        records.extend(body["data"])
        page = body["next_page"]
    return records

print("short-page rule:", [o["id"] for o in fetch_short_page_rule(client)])
print("next_page rule: ", [o["id"] for o in fetch_next_page_rule(client)])
```
```text
short-page rule: [101, 102, 103, 105, 106]
next_page rule:  [101, 102, 103, 105, 106, 107]
```

Page 2 had only two visible orders (104 is cancelled and was filtered out), so the short-page loop decided page 2 was the last one, stopped, and lost order 107 without any error. With a real API of a thousand pages, it would have lost every page after the first short one. The `next_page` loop got every visible order.

### 3.7 Safety limits: never trust "next" forever

What if the server has a bug and always says there is a next page? Your `while page is not None` loop runs forever, making requests until something runs out: your rate limit, your memory, or someone's patience. A careful loop has a **safety limit**: a maximum number of pages after which it stops and raises a clear error. It must **raise**, not quietly return what it has, because returning a partial result looks exactly like success.

```python
import httpx

class TooManyPages(Exception):
    pass

def endless_handler(request):
    page = int(request.url.params.get("page", "1"))
    return httpx.Response(200, json={"data": [{"id": page}], "next_page": page + 1})   # never None

def fetch_all_pages_guarded(client, max_pages=50):
    records, page, fetched = [], 1, 0
    while page is not None:
        if fetched == max_pages:
            raise TooManyPages(f"stopped after {max_pages} pages; next_page was still {page}. "
                               "Is the API looping, or should max_pages be raised?")
        body = client.get("/v1/orders", params={"page": page}).raise_for_status().json()
        fetched += 1
        records.extend(body["data"])
        page = body["next_page"]
    return records

client = httpx.Client(transport=httpx.MockTransport(endless_handler), base_url="https://api.pagebound.test")
try:
    fetch_all_pages_guarded(client, max_pages=5)
except TooManyPages as error:
    print(error)

print(len(fetch_all_pages_guarded(make_client(), max_pages=5)), "orders from the normal API (3 pages, under the limit)")
```
```text
stopped after 5 pages; next_page was still 6. Is the API looping, or should max_pages be raised?
7 orders from the normal API (3 pages, under the limit)
```

Pick the limit generously: well above the largest real number of pages (say ten times), so it never fires on a normal day. Its job is to turn "runs forever" into "fails loudly within minutes".

A related guard catches a server that returns the **same** cursor or next URL twice. If `next_cursor` equals the cursor you just sent, the server is looping, and you can raise at once instead of waiting for the page limit:

```python
if body["next_cursor"] == params.get("cursor"):
    raise RuntimeError(f"cursor did not advance: {body['next_cursor']!r}")
```

### 3.8 Why offset pagination skips and duplicates rows when data changes

Pages are fetched one after another, seconds or minutes apart. Meanwhile the data keeps changing: new orders arrive, old ones are deleted. With **offset** pagination, any change to the rows **before** your current position shifts every later row by one, and you either see a row twice or never see it.

Here is the effect, run for real. The API lists orders **newest first** (a very common default) with offset pagination. Between our first and second request, a new order 108 is placed:

```python
import httpx

store = sorted(ORDERS, key=lambda o: o["id"], reverse=True)       # newest first: 107, 106, ...
calls = []

def changing_handler(request):
    calls.append(1)
    if len(calls) == 2:                                            # a new order arrives before page 2
        store.insert(0, {"id": 108})
    offset = int(request.url.params["offset"])
    return httpx.Response(200, json={"data": [{"id": o["id"]} for o in store[offset:offset + 3]]})

client = httpx.Client(transport=httpx.MockTransport(changing_handler), base_url="https://api.pagebound.test")
seen = []
for offset in (0, 3, 6):
    page = client.get("/v1/orders", params={"offset": offset, "limit": 3}).json()["data"]
    print("offset", offset, "->", [o["id"] for o in page])
    seen.extend(o["id"] for o in page)
print("collected:", seen)
print("duplicates:", sorted({i for i in seen if seen.count(i) > 1}), "| not collected:", sorted({o["id"] for o in store} - set(seen)))
```
```text
offset 0 -> [107, 106, 105]
offset 3 -> [105, 104, 103]
offset 6 -> [102, 101]
collected: [107, 106, 105, 105, 104, 103, 102, 101]
duplicates: [105] | not collected: [108]
```

Order 105 appears twice. It was the last order on page 1; then the new order 108 pushed every row down by one position, so when we asked for "skip 3", order 105 was now in position 4 and came back again as the first order of page 2. (Order 108 itself was not collected, because it arrived at the front after we had passed it. That part is fine: the next run will see it.) If instead an order had been **deleted** from the first page, everything would shift up and one order would be **skipped**, which is worse, because a skipped record is invisible:

```python
store[:] = sorted(ORDERS, key=lambda o: o["id"], reverse=True)
calls.clear()

def deleting_handler(request):
    calls.append(1)
    if len(calls) == 2:
        store.remove(next(o for o in store if o["id"] == 106))     # order 106 is deleted before page 2
    offset = int(request.url.params["offset"])
    return httpx.Response(200, json={"data": [{"id": o["id"]} for o in store[offset:offset + 3]]})

client = httpx.Client(transport=httpx.MockTransport(deleting_handler), base_url="https://api.pagebound.test")
seen = []
for offset in (0, 3, 6):
    seen.extend(o["id"] for o in client.get("/v1/orders", params={"offset": offset, "limit": 3}).json()["data"])
print("collected:", seen)
print("never seen although it still exists:", sorted({o["id"] for o in ORDERS} - set(seen) - {106}))
```
```text
collected: [107, 106, 105, 103, 102, 101]
never seen although it still exists: [104]
```

Order 104 still exists, nobody deleted it, and we never saw it. With a real pipeline, that order would simply be missing from finance's report.

**Keyset (cursor) pagination does not have this problem**, because each page asks "give me rows **after id X**" instead of "skip N rows". Inserting or deleting other rows does not change which rows come after X. That is the main reason modern APIs use cursors. If you must use an offset API, three things reduce the damage:

- sort by something that does not change and grows with time (oldest first, by id or creation time), so new rows land at the **end**;
- use incremental loads with an overlap (section 8), so a record missed this run is picked up next run;
- deduplicate on the key (section 9), so a record seen twice is stored once.

### 3.9 Pages as a generator

The functions above collect every record into one list before returning. For seven orders that is fine. For ten million it is not, and it also means nothing can be saved until the very last page arrives. A **generator** that yields one page at a time lets the caller process and save each page as it comes, keeping memory flat and making resume possible:

```python
def iter_pages(client, per_page=3, max_pages=1000):
    page, fetched = 1, 0
    while page is not None:
        if fetched == max_pages:
            raise RuntimeError(f"more than {max_pages} pages")
        body = client.get("/v1/orders", params={"page": page, "per_page": per_page}).raise_for_status().json()
        fetched += 1
        yield page, body["data"]
        page = body["next_page"]

for page, data in iter_pages(make_client()):
    print("page", page, "->", [o["id"] for o in data], "(save this page now)")
```
```text
page 1 -> [101, 102, 103] (save this page now)
page 2 -> [104, 105, 106] (save this page now)
page 3 -> [107] (save this page now)
```

The rest of the chapter uses this shape: **fetch a page, process it, save it, record progress, then fetch the next**.

### 3.10 Try it: pagination

**Try it 7.** Predict the output. This loop has a bug. Which pages does it request, and how many orders does it collect from the fake API (7 orders, 3 per page)?

```python
log = []
client = make_client(log=log)
records, page = [], 1
while True:
    body = client.get("/v1/orders", params={"page": page, "per_page": 3}).json()
    if body["next_page"] is None:
        break
    records.extend(body["data"])
    page = body["next_page"]
print([e["page"] for e in log], len(records))
```

<details><summary>Answer</summary>

```python
log = []
client = make_client(log=log)
records, page = [], 1
while True:
    body = client.get("/v1/orders", params={"page": page, "per_page": 3}).json()
    if body["next_page"] is None:
        break
    records.extend(body["data"])
    page = body["next_page"]
print([e["page"] for e in log], len(records))
```
```text
['1', '2', '3'] 6
```

It requests pages 1, 2 and 3, but breaks out **before** adding page 3's data, so it keeps only 6 of the 7 orders. The stop check must come **after** using the page: take the data, then decide whether to continue. A good test for every pagination loop is a data set whose last page has something on it.

</details>

**Try it 8.** An offset API returns `{"data": [...], "total": 250}` and you page with `limit=100`. The loop stops when `offset >= total`. During the run, 5 orders are deleted. What can go wrong, and what stop rule is safer?

<details><summary>Answer</summary>

Two things. First, deletions shift later rows up, so some rows are skipped (section 3.8). Second, if you read `total` only from the first page (250), you make three requests (offsets 0, 100, 200), which is still fine here; but if orders were **added**, a total read once is too small and you stop early, missing the new tail. Safer: read `total` from every response, or better, keep requesting until a page comes back **empty**. Best: ask for keyset/cursor pagination, or sort oldest-first so changes land at the end, and rely on incremental re-runs and dedupe to repair the rest.

</details>

**Try it 9.** Why must `fetch_all_pages_guarded` **raise** when it reaches `max_pages`, instead of `break` and return the records it has?

<details><summary>Answer</summary>

Because the caller cannot tell a partial result from a complete one. If it returns quietly, the pipeline loads 50 pages, saves its watermark or checkpoint as if the run finished, and the missing data is never fetched; every report looks normal and is wrong. Raising stops the run, nothing is marked as done, and a human sees a clear message ("stopped after 50 pages; next_page was still 51"). Failing loudly is always better than succeeding wrongly.

</details>

**Try it 10.** In `fetch_all_cursor`, a colleague "simplifies" the loop to compute the next cursor on the client: `params["cursor"] = encode_cursor(records[-1]["id"])`. It works today. Give two reasons it is a bad idea.

<details><summary>Answer</summary>

1. The cursor is **opaque** by contract. The API team may change its format (add a sort key, sign it, encrypt it, expire it) at any time, and client-built cursors will break or, worse, silently return the wrong rows.
2. The server may sort or filter in ways the client does not know (for example by `updated_at` and then `id`), so "after the last id I received" may not be the right position. Only the server knows where the next page starts. Pass back exactly the `next_cursor` you were given.

</details>

## 4. ETL vs ELT

### 4.1 Same three steps, two orders

Extract, transform, load can happen in two orders, and each has a name.

- **ETL (Extract, Transform, Load)**: fetch the data, clean and reshape it **in your program** (Python), and load only the finished result into the destination.
- **ELT (Extract, Load, Transform)**: fetch the data and load it **as it is** into the destination first; then transform it **inside the database**, usually with SQL.

```text
ETL:  API --> Python: flatten, parse, check --> clean table
ELT:  API --> raw table (JSON text, untouched) --> SQL: INSERT INTO clean SELECT ... FROM raw
```

Neither is "the right one". ETL was the norm when databases were expensive and you only wanted to store tidy data. ELT became popular when storage got cheap and warehouses got fast at SQL: load everything, decide later. Most real pipelines are a mix.

### 4.2 ETL in Python

In ETL the Python code does the reshaping. Here is a minimal version: fetch all pages, turn each nested order into one flat row, and load the rows.

```python
import sqlite3

def to_row(order):
    return (order["id"], order["customer"]["email"], order["customer"]["city"],
            order["status"], order["amount"], order["created_at"], len(order["items"]))

con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE orders_clean (
    id INTEGER PRIMARY KEY, email TEXT, city TEXT, status TEXT,
    amount TEXT, created_at TEXT, item_lines INTEGER)""")

client = make_client()
page = 1
while page is not None:
    body = client.get("/v1/orders", params={"page": page}).raise_for_status().json()
    with con:
        con.executemany("INSERT OR IGNORE INTO orders_clean VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [to_row(o) for o in body["data"]])
    page = body["next_page"]

for row in con.execute("SELECT id, city, status, item_lines FROM orders_clean WHERE id <= 103"):
    print(row)
```
```text
(101, 'Pune', 'shipped', 1)
(102, None, 'pending', 1)
(103, 'Delhi', 'shipped', 2)
```

(`INSERT OR IGNORE` skips rows whose primary key already exists. It is a quick way to keep this example re-runnable; section 9 explains why "only if newer" is usually better.)

The database only ever sees clean rows. If `to_row` raises on a bad record, nothing about that record reaches the database.

### 4.3 ELT in SQLite: raw first, then SQL

In ELT you first store each record **exactly as it arrived**, as JSON text, with a little bookkeeping: when it was fetched and by which run. That table is called the **raw** layer.

```python
import json
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE raw_orders (
    id INTEGER PRIMARY KEY,      -- the record's key, pulled out so we can upsert
    body TEXT NOT NULL,          -- the JSON exactly as received
    fetched_at TEXT NOT NULL,
    run_id TEXT NOT NULL)""")

def load_raw(con, records, run_id, fetched_at):
    with con:
        con.executemany(
            "INSERT INTO raw_orders (id, body, fetched_at, run_id) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET body = excluded.body, "
            "fetched_at = excluded.fetched_at, run_id = excluded.run_id",
            [(r["id"], json.dumps(r), fetched_at, run_id) for r in records],
        )

client = make_client()
page = 1
while page is not None:
    body = client.get("/v1/orders", params={"page": page}).raise_for_status().json()
    load_raw(con, body["data"], run_id="run-001", fetched_at="2024-06-05T00:00:00Z")
    page = body["next_page"]

print(con.execute("SELECT COUNT(*) FROM raw_orders").fetchone())
print(con.execute("SELECT body FROM raw_orders WHERE id = 102").fetchone()[0])
```
```text
(7,)
{"id": 102, "customer": {"email": "ben@example.com", "city": null}, "status": "pending", "amount": "5.50", "currency": "INR", "created_at": "2024-06-01T11:30:00Z", "updated_at": "2024-06-01T12:30:00Z", "items": [{"sku": "B2", "qty": 1}]}
```

Raw text is stored as received, so it can be broken. SQLite's `json_valid(text)` returns 1 for well-formed JSON and 0 otherwise, which lets the transform skip (or count) broken rows instead of failing on them. (`json_extract` on invalid JSON raises an error, `malformed JSON`, and stops the whole statement.)

```python
for text in ['{"id": 1}', '{"id": 1', 'not json', '[1, 2, 3]']:
    print(f"{text!r:12}", con.execute("SELECT json_valid(?)", (text,)).fetchone()[0])
try:
    con.execute("SELECT json_extract('{\"id\": 1', '$.id')").fetchone()
except sqlite3.OperationalError as error:
    print("json_extract on broken text:", error)
```
```text
'{"id": 1}'  1
'{"id": 1'   0
'not json'   0
'[1, 2, 3]'  1
json_extract on broken text: malformed JSON
```

Now the transform is SQL. SQLite's JSON functions read inside the text: `json_extract(body, '$.customer.city')` follows the path `customer` → `city`, and `json_array_length(body, '$.items')` counts the items. The whole clean table is built by one statement:

```python
con.execute("""CREATE TABLE orders_clean (
    id INTEGER PRIMARY KEY, email TEXT, city TEXT, status TEXT,
    amount_cents INTEGER, created_at TEXT, item_lines INTEGER)""")

def build_clean(con):
    with con:
        con.execute("DELETE FROM orders_clean")
        con.execute("""
            INSERT INTO orders_clean
            SELECT id,
                   lower(json_extract(body, '$.customer.email')),
                   json_extract(body, '$.customer.city'),
                   json_extract(body, '$.status'),
                   CAST(round(CAST(json_extract(body, '$.amount') AS REAL) * 100) AS INTEGER),
                   json_extract(body, '$.created_at'),
                   json_array_length(body, '$.items')
            FROM raw_orders
            WHERE json_valid(body)
        """)

build_clean(con)
for row in con.execute("SELECT * FROM orders_clean ORDER BY id LIMIT 3"):
    print(row)
```
```text
(101, 'asha@example.com', 'Pune', 'shipped', 1999, '2024-06-01T10:00:00Z', 1)
(102, 'ben@example.com', None, 'pending', 550, '2024-06-01T11:30:00Z', 1)
(103, 'chen@example.com', 'Delhi', 'shipped', 4200, '2024-06-02T09:15:00Z', 2)
```

Look at the money column: `CAST(round(CAST(json_extract(body, '$.amount') AS REAL) * 100) AS INTEGER)` reads the text `"19.99"`, turns it into a number, multiplies by 100, **rounds** (because `19.99 * 100` as a float is `1998.9999999999998`, and a plain `CAST` to `INTEGER` would truncate it to 1998), and stores whole cents. You can see the truncation for yourself:

```python
print(con.execute("""SELECT CAST(CAST('19.99' AS REAL) * 100 AS INTEGER),
                            CAST(round(CAST('19.99' AS REAL) * 100) AS INTEGER)""").fetchone())
```
```text
(1998, 1999)
```

The `WHERE json_valid(body)` keeps a broken raw row from stopping the whole rebuild; a real pipeline would also count such rows and report them.

Notice the `DELETE` and `INSERT` happen in one transaction (`with con:`), so the clean table is rebuilt **atomically**: someone reading it sees either the old version or the new one, never an empty table halfway through. And notice `city` came out as `None` for order 102: JSON `null` becomes SQL `NULL`.

(The money conversion goes through `REAL` and `round`, which is acceptable for two-decimal amounts of normal size, but section 5.2 explains why the Python side should use `Decimal`.)

### 4.4 Layers: raw, staging, clean

Bigger pipelines name their layers. The names vary between companies, but the idea is the same:

| Layer | Also called | What it holds | Who reads it |
|---|---|---|---|
| **raw** | landing, bronze | records exactly as received, plus fetch time and run id | the pipeline only; for replays and debugging |
| **staging** | silver | parsed, typed, checked, deduplicated rows | the pipeline; data engineers |
| **clean** | mart, gold, reporting | business-ready tables: one row per order, daily totals | analysts, finance, dashboards |

You can build every layer with the tools you have: a raw table of JSON text, a staging table filled by Python or SQL, and clean tables built with `INSERT ... SELECT` and `GROUP BY`.

### 4.5 Keeping raw data lets you replay

The strongest argument for ELT (or for storing raw data even in an ETL pipeline) is the **replay**. Suppose the clean table was built for weeks, and then finance asks: "we also need the customer's city in lowercase, and the total quantity of books per order". Without raw data, you must re-fetch weeks of history from the API, which may not even keep it. With raw data, you change the SQL and rebuild:

```python
con.execute("ALTER TABLE orders_clean ADD COLUMN qty_total INTEGER")
with con:
    con.execute("""
        UPDATE orders_clean SET
            city = lower(city),
            qty_total = (SELECT SUM(json_extract(item.value, '$.qty'))
                         FROM raw_orders AS r, json_each(r.body, '$.items') AS item
                         WHERE r.id = orders_clean.id)
    """)
for row in con.execute("SELECT id, city, item_lines, qty_total FROM orders_clean ORDER BY id"):
    print(row)
print("API calls needed for this change: 0")
```
```text
(101, 'pune', 1, 2)
(102, None, 1, 1)
(103, 'delhi', 2, 4)
(104, 'mumbai', 1, 1)
(105, 'pune', 1, 2)
(106, 'chennai', 2, 2)
(107, 'pune', 1, 1)
API calls needed for this change: 0
```

`json_each(body, '$.items')` is a SQLite **table-valued function**: it turns a JSON array into rows, one per element, with the element in a column called `value`. Here it turns each order's `items` list into rows so `SUM` can add up the `qty` fields. You will not need it often, but it is good to know that "unnest a JSON list in SQL" is possible.

### 4.6 When each fits

| Situation | Better fit | Why |
|---|---|---|
| The destination is a powerful SQL database, and analysts write SQL | ELT | Transforms are easy to change and re-run inside the database. |
| The data contains things that must **never** be stored (card numbers, passwords) | ETL | Remove them before they touch the disk. Raw storage would keep them forever. |
| You expect the transform rules to change often | ELT, or ETL that also keeps raw | Replay from raw instead of re-fetching. |
| The transform needs Python (calls a library, complex parsing, machine learning) | ETL | SQL cannot do it, or does it badly. |
| The source is huge and you only need a small part | ETL | Filter early; do not pay to store what you will throw away. |
| You must prove later exactly what the source sent | ELT (raw kept) | The raw layer is the evidence. |

The pipelines in this chapter keep a raw copy when it is cheap and safe, do typed parsing and checks in Python (because Python's `Decimal` and `datetime` are stricter and better tested than SQL string tricks), and use SQL for upserts and aggregations.

### 4.7 Try it: ETL and ELT

**Try it 11.** Using the `raw_orders` table from section 4.3, write one SQL query that returns each `status` and the number of orders with that status, straight from the JSON text, ordered by status.

<details><summary>Answer</summary>

```python
for row in con.execute("""
    SELECT json_extract(body, '$.status') AS status, COUNT(*) AS n
    FROM raw_orders
    GROUP BY status
    ORDER BY status"""):
    print(row)
```
```text
('cancelled', 1)
('pending', 2)
('shipped', 4)
```

`json_extract` works anywhere an expression is allowed, including `GROUP BY`. In ELT, analysts can explore the raw layer like this before anyone has designed a clean table.

</details>

**Try it 12.** For each scenario, choose ETL or ELT and give one reason. (a) A payments API sends full card numbers that your company is not allowed to store. (b) A marketing team keeps changing its mind about how "active customer" is defined. (c) An API returns PDF invoices, and you need the total printed inside each PDF.

<details><summary>Answer</summary>

(a) **ETL**: the card number must be removed (or never requested) before anything is written; a raw layer would store it, and it would be copied into backups. (b) **ELT** (keep raw): the definition is a SQL query over raw or staging data, so each change is a rebuild, not a re-fetch. (c) **ETL**: reading text out of a PDF needs a Python library; SQL cannot do it. You might still keep the PDFs (raw) for replays.

</details>

## 5. Transform: flatten, parse, normalise

### 5.1 Flattening nested JSON

API records are trees: an order contains a customer, which contains an email; an order contains a list of items. A SQL table or a CSV file is flat: rows and columns. **Flattening** turns the tree into columns.

There are two cases, and they need different answers:

1. **A nested object** (one customer per order): pull its fields up with a prefix. `customer.email` becomes `customer_email`, `customer.city` becomes `customer_city`. One record still makes one row.
2. **A nested list** (many items per order): you cannot put a list in one cell. Either **summarise** it into the order row (number of item lines, total quantity), or make a **second table** with one row per item, keyed by `(order_id, sku)` or `(order_id, line_number)`. The second table is the normalised design from the last chapter; the summary is convenient for reporting. Many pipelines do both.

```python
def flatten_customer(order):
    customer = order.get("customer") or {}
    return {"id": order["id"],
            "customer_email": customer.get("email"),
            "customer_city": customer.get("city")}

def item_rows(order):
    return [{"order_id": order["id"], "line": n, "sku": item["sku"], "qty": item["qty"]}
            for n, item in enumerate(order["items"], start=1)]

print(flatten_customer(ORDERS[2]))
for row in item_rows(ORDERS[2]):
    print(row)
```
```text
{'id': 103, 'customer_email': 'chen@example.com', 'customer_city': 'Delhi'}
{'order_id': 103, 'line': 1, 'sku': 'B1', 'qty': 1}
{'order_id': 103, 'line': 2, 'sku': 'B3', 'qty': 3}
```

Order 103 has two item lines, so it makes one order row and two item rows. If you put item fields directly into the order row (for example `sku_1`, `sku_2`, ...), you get a table with a different number of columns for every order. Do not do that.

`order.get("customer") or {}` protects against a missing or `null` customer. Whether a missing customer should be tolerated or treated as a bad record is a decision for the contract (section 6), not for the flattening code. Write the flattening so it does not crash, and let the checks decide.

### 5.2 Money: `Decimal`, never float

The API sends `"amount": "19.99"` as a string. The tempting move is `float("19.99")`. Here is why that is wrong:

```python
print(0.1 + 0.2)
print(float("1.10") + float("2.20"))
total = 0.0
for _ in range(10):
    total += float("0.10")              # ten payments of 0.10, added one by one
print(total)
print(round(2.675, 2))
print(sum(float(o["amount"]) for o in ORDERS))
```
```text
0.30000000000000004
3.3000000000000003
0.9999999999999999
2.67
132.49
```

A float is stored in binary, and most decimal fractions (0.1, 19.99) have no exact binary form, just as 1/3 has no exact decimal form. The tiny errors appear when you add, multiply, round or compare. Ten payments of 0.10 add up to `0.9999999999999999`, so a check like `total == 1.0` fails on values that "look" equal; `round(2.675, 2)` gives 2.67 because the float nearest to 2.675 is slightly below it. (Python's built-in `sum()` has used a more careful algorithm for floats since Python 3.12 and would print `1.0` for those ten payments; but running totals in real code are usually `+=` in a loop, or computed by SQL or other tools, and no careful adding can fix `round(2.675, 2)`.) The last line shows the danger best: our seven real orders happen to add up to a clean-looking `132.49`, so a float pipeline passes every test on this data and then fails on next week's data. Errors that appear only for some values are the hardest kind to catch.

`decimal.Decimal` stores decimal digits exactly:

```python
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

amounts = [Decimal(o["amount"]) for o in ORDERS]
print(sum(amounts))
print(Decimal("1.10") + Decimal("2.20"))
print(sum([Decimal("0.10")] * 10))
print(Decimal("5.50"), Decimal("5.50") == Decimal("5.5"))
tax = Decimal("19.99") * Decimal("0.18")
print(tax, "->", tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
```
```text
132.49
3.30
1.00
5.50 True
3.5982 -> 3.60
```

Three rules for money:

1. **Create a `Decimal` from a string, never from a float.** `Decimal("19.99")` is exact; `Decimal(19.99)` faithfully copies the float's binary error (Try it 13).
2. **Round on purpose**, with `quantize` and a named rounding mode, at the point the business rules say (for example, once per line item, or once per invoice).
3. **Bad text raises `InvalidOperation`**, not `ValueError`. Your per-record error handling must catch it.

```python
for text in ["12.50", " 7 ", "N/A", "", "1,200.00"]:
    try:
        print(repr(text), "->", Decimal(text))
    except InvalidOperation:
        print(repr(text), "-> InvalidOperation")
```
```text
'12.50' -> 12.50
' 7 ' -> 7
'N/A' -> InvalidOperation
'' -> InvalidOperation
'1,200.00' -> InvalidOperation
```

`Decimal` ignores surrounding spaces, but rejects the empty string and thousands separators. If an API sends `"1,200.00"`, decide explicitly whether to strip commas (and document it), instead of letting it fail randomly.

**`InvalidOperation` is not a `ValueError`.** This surprises almost everyone. `int("abc")` and `float("abc")` raise `ValueError`, so you would expect `Decimal("abc")` to do the same. It does not: `InvalidOperation` belongs to the `ArithmeticError` family, and an `except ValueError` walks straight past it.

```python
print(issubclass(InvalidOperation, ValueError), issubclass(InvalidOperation, ArithmeticError))
print([cls.__name__ for cls in InvalidOperation.__mro__])

def parse_amount_wrong(text):
    try:
        return Decimal(text)
    except ValueError:                   # looks right, catches nothing here
        return None

parse_amount_wrong("abc")
```
```text
False True
['InvalidOperation', 'DecimalException', 'ArithmeticError', 'Exception', 'BaseException', 'object']
Traceback (most recent call last):
  ...
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
```

So any per-record handler that parses money must list `InvalidOperation` explicitly (section 7.3 does).

Two more surprises in what `Decimal` **accepts**:

```python
for text in ["1e3", "NaN", "-Infinity", "0.1E-1"]:
    value = Decimal(text)
    print(f"{text!r:12} -> {value!s:10} finite={value.is_finite()}")
print(Decimal("1e3") == 1000, Decimal("1e3").quantize(Decimal("0.01")))
```
```text
'1e3'        -> 1E+3       finite=True
'NaN'        -> NaN        finite=False
'-Infinity'  -> -Infinity  finite=False
'0.1E-1'     -> 0.01       finite=True
True 1000.00
```

Scientific notation is valid input, and the value keeps its exponent, so `Decimal("1e3")` **prints** as `1E+3` even though it equals 1000 (`quantize` gives the normal `1000.00` form). And `"NaN"` and `"Infinity"` parse without any error at all. A money parser should therefore also check `value.is_finite()` (and, usually, that there are at most two decimal places), or a record with `"amount": "NaN"` sails through and poisons every sum it touches.

**Storing money in SQLite.** SQLite has no decimal type. A column declared `DECIMAL(10,2)` gets NUMERIC affinity and may store `19.99` as a REAL, bringing the float problem back. Two safe choices:

- Store **integer minor units** (cents, paise): `amount_cents INTEGER`, computed as `int(amount * 100)` from a `Decimal` that has at most two decimal places. Sums of integers are exact. This is the most common choice.
- Store the **text** `'19.99'` and convert back to `Decimal` in Python. Exact, but SQL `SUM` on text converts to REAL again, so totals must be done in Python.

```python
def to_cents(amount: Decimal) -> int:
    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError(f"more than 2 decimal places: {amount}")
    return int(amount * 100)

print([to_cents(a) for a in amounts], sum(to_cents(a) for a in amounts))
print(Decimal(sum(to_cents(a) for a in amounts)) / 100)
```
```text
[1999, 550, 4200, 1225, 775, 3000, 1500] 13249
132.49
```

### 5.3 Dates and times with time zones

The API sends `"created_at": "2024-06-01T10:00:00Z"`. This is **ISO 8601** text; the `Z` (for "Zulu") means UTC. Since Python 3.11, `datetime.fromisoformat` reads it directly:

```python
from datetime import datetime, timedelta, timezone

created = datetime.fromisoformat("2024-06-01T10:00:00Z")
print(repr(created))
print(created.tzinfo, created.utcoffset())
```
```text
datetime.datetime(2024, 6, 1, 10, 0, tzinfo=datetime.timezone.utc)
UTC 0:00:00
```

The result is **aware**: it knows its time zone. A datetime without a time zone is **naive**: it is just a wall-clock reading with no idea where on Earth it was read. Python refuses to compare the two, because the answer would be a guess:

```python
naive = datetime(2024, 6, 1, 10, 0)
print(naive.tzinfo)
naive < created
```
```text
None
Traceback (most recent call last):
  ...
TypeError: can't compare offset-naive and offset-aware datetimes
```

That `TypeError` is a gift: it stops you from mixing "10:00 in Pune" with "10:00 in London" by accident. The rule in pipelines is: **parse every timestamp to an aware datetime, convert it to UTC, and keep it in UTC until the moment you show it to a person.**

```python
IST = timezone(timedelta(hours=5, minutes=30), "IST")

def parse_ts(text: str) -> datetime:
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise ValueError(f"timestamp has no time zone: {text!r}")
    return value.astimezone(timezone.utc)

print(parse_ts("2024-06-01T10:00:00Z"))
print(parse_ts("2024-06-01T15:30:00+05:30"))         # the same instant, written in IST
print(parse_ts("2024-06-01T10:00:00Z") == parse_ts("2024-06-01T15:30:00+05:30"))
print(parse_ts("2024-06-01T10:00:00Z").astimezone(IST))
```
```text
2024-06-01 10:00:00+00:00
2024-06-01 10:00:00+00:00
True
2024-06-01 15:30:00+05:30
```

Both strings describe the same instant, so the parsed values are equal. This is why comparing timestamps **as text** (as our fake server does) is fragile: `"2024-06-01T10:00:00Z"` and `"2024-06-01T15:30:00+05:30"` are different strings for the same moment.

**Which day is it?** Daily reports and partitions (section 14) need a date. The date depends on the time zone. An order placed at 20:00 UTC on 1 June is placed at 01:30 on **2 June** in India:

```python
late = parse_ts("2024-06-01T20:00:00Z")
print("UTC date:", late.date(), "| IST date:", late.astimezone(IST).date())
```
```text
UTC date: 2024-06-01 | IST date: 2024-06-02
```

Neither is wrong, but the pipeline must pick one, write it down ("order_date is the date in IST"), and use it everywhere. Mixing them makes daily totals disagree between two reports.

(We use a fixed offset `timezone(timedelta(hours=5, minutes=30))` for India, which has no daylight saving. For places with daylight saving, use `zoneinfo.ZoneInfo("Europe/London")`; on Windows that needs the `tzdata` package installed.)

**Storing timestamps.** In SQLite, store UTC timestamps as ISO text in **one fixed format**, such as `2024-06-01T10:00:00+00:00` (`datetime.isoformat()` of a UTC value). Text in one fixed format sorts in time order, so `ORDER BY` and `MAX()` work. In Parquet, use a real timestamp type (section 13).

### 5.4 Normalising strings

The same value can arrive in many spellings: `"Asha@Example.com "`, `"asha@example.com"`. If you do not normalise, a `GROUP BY email` counts one customer as two. Normalising means choosing one canonical form:

```python
def clean_email(value):
    if value is None:
        return None
    value = value.strip().lower()
    return value or None                         # "" becomes None

def clean_city(value):
    if value is None:
        return None
    value = " ".join(value.split())              # trim and collapse inner spaces
    return value.title() or None

def clean_status(value):
    return value.strip().lower() if isinstance(value, str) else value

for raw in ["  Asha@Example.COM ", "", None]:
    print(repr(raw), "->", repr(clean_email(raw)))
print(repr(clean_city("  new   delhi ")), repr(clean_city("   ")), repr(clean_status(" Shipped")))
```
```text
'  Asha@Example.COM ' -> 'asha@example.com'
'' -> None
None -> None
'New Delhi' None 'shipped'
```

Points to keep in mind:

- **Decide what empty means.** An empty string and `None` usually mean the same ("no value"), so turn `""` into `None` once, early, and the rest of the code only checks for `None`.
- **Normalise for matching, not for display.** Lowercasing an email is safe (in practice). Title-casing names is not: it turns "McDonald" into "Mcdonald". Only normalise fields where you know the rule.
- **Do not "fix" values you do not understand.** Turning an unknown status `"lost"` into `"cancelled"` is inventing data. Unknown values belong in quarantine (section 7), not in a guess.

### 5.5 A complete transform function

Putting the pieces together: one function that turns a raw API order into a flat, typed, normalised row. It raises a clear error when something cannot be parsed. It does no I/O at all.

```python
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

IST = timezone(timedelta(hours=5, minutes=30), "IST")
STATUSES = {"shipped", "pending", "cancelled"}

def parse_ts(text):
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise ValueError(f"timestamp has no time zone: {text!r}")
    return value.astimezone(timezone.utc)

def flatten_order(order):
    """Raw API order -> flat typed row. Raises ValueError/KeyError/TypeError/InvalidOperation on bad data."""
    customer = order["customer"] or {}
    email = (customer.get("email") or "").strip().lower() or None
    city = customer.get("city")
    if isinstance(city, str):
        city = " ".join(city.split()).title() or None
    status = order["status"].strip().lower()
    if status not in STATUSES:
        raise ValueError(f"unknown status {order['status']!r}")
    amount = Decimal(order["amount"])
    created = parse_ts(order["created_at"])
    return {
        "id": order["id"],
        "customer_email": email,
        "customer_city": city,
        "status": status,
        "amount": amount,
        "currency": order["currency"],
        "created_at": created,
        "updated_at": parse_ts(order["updated_at"]),
        "order_date": created.astimezone(IST).date().isoformat(),
        "item_lines": len(order["items"]),
        "qty_total": sum(item["qty"] for item in order["items"]),
    }
```

```python
from pprint import pprint
pprint(flatten_order(ORDERS[2]), sort_dicts=False)
```
```text
{'id': 103,
 'customer_email': 'chen@example.com',
 'customer_city': 'Delhi',
 'status': 'shipped',
 'amount': Decimal('42.00'),
 'currency': 'INR',
 'created_at': datetime.datetime(2024, 6, 2, 9, 15, tzinfo=datetime.timezone.utc),
 'updated_at': datetime.datetime(2024, 6, 2, 9, 15, tzinfo=datetime.timezone.utc),
 'order_date': '2024-06-02',
 'item_lines': 2,
 'qty_total': 4}
```

Read the output line by line: `amount` is a `Decimal`, the timestamps are aware UTC datetimes, `order_date` is the IST date as text (ready to be a partition key), and the item list has become two numbers. `flatten_order` is defined as part of this chapter's shared setup, so later sections can use it.

### 5.6 Keep transforms pure

`flatten_order` takes a dictionary and returns a dictionary. It does not call the API, read files, write to the database, look at the clock or log anything. A function like that is **pure**, and pure transforms are the easiest part of a pipeline to get right:

- **Testing is trivial**: give it a dict, compare the output. No mock server, no temp folder.
- **Errors point at data**: if it raises, the record is bad (or the function has a bug); it is never "the network was slow".
- **It can be re-run any number of times**, on raw data saved last month, and gives the same answer.

When a transform needs "now" (for example, to compute an order's age), pass `now` in as an argument instead of calling `datetime.now()` inside. Then tests can pass a fixed time and get repeatable results. You will see this "inject the clock" pattern again for retries (inject `sleep`) and randomness (inject `rand`).

### 5.7 Try it: transforms

**Try it 13.** Predict what these print. Then explain the difference.

```python
from decimal import Decimal
print(Decimal("19.99"))
print(Decimal(19.99))
print(Decimal(19.99) == Decimal("19.99"))
```

<details><summary>Answer</summary>

```python
from decimal import Decimal
print(Decimal("19.99"))
print(Decimal(19.99))
print(Decimal(19.99) == Decimal("19.99"))
```
```text
19.99
19.989999999999998436805981327779591083526611328125
False
```

`Decimal(19.99)` first creates the float `19.99`, which in binary is really 19.989999999999998436805981327779591083526611328125, and `Decimal` copies that exact value. The string version is exactly 19.99. Always build money from the string the API sent.

</details>

**Try it 14.** An order has `"created_at": "2024-06-30T19:15:00Z"`. What is its `order_date` in `flatten_order`? Would a June revenue report built on UTC dates include it? One built on IST dates?

<details><summary>Answer</summary>

```python
created = parse_ts("2024-06-30T19:15:00Z")
print(created.date(), created.astimezone(IST).date())
```
```text
2024-06-30 2024-07-01
```

19:15 UTC is 00:45 the next day in IST, so `order_date` is `2024-07-01`. A UTC-based June report includes the order; an IST-based one puts it in July. Neither is wrong; the pipeline must choose one definition and use it everywhere, or the two reports will disagree by exactly the orders placed between 18:30 and 24:00 UTC on the last day of the month.

</details>

**Try it 15.** Run `flatten_order` on order 102 (whose city is `null`). Which fields are `None`? Then predict what happens for a copy of order 101 whose `amount` is `"19,99"` (a European decimal comma).

<details><summary>Answer</summary>

```python
import copy
row = flatten_order(ORDERS[1])
print({k: v for k, v in row.items() if v is None})
bad = copy.deepcopy(ORDERS[0])
bad["amount"] = "19,99"
try:
    flatten_order(bad)
except InvalidOperation as error:
    print("InvalidOperation:", error)
```
```text
{'customer_city': None}
InvalidOperation: [<class 'decimal.ConversionSyntax'>]
```

Only `customer_city` is `None`. For `"19,99"`, `Decimal` raises `InvalidOperation`. Its message is a list containing the exception class, which is not helpful, so section 7 wraps it in a message that names the field and the bad value. (Note `copy.deepcopy`: a plain `dict(ORDERS[0])` would share the nested `customer` dict and `items` list with the original, and editing them would change the shared test data.)

</details>

## 6. Schema checks and data-quality checks

### 6.1 Contracts: write down what a record must look like

A **schema** (or **data contract**) is a written description of what a valid record looks like: which fields exist, what type each has, which may be null, and which values are allowed. Without one, every function in the pipeline makes its own silent assumptions, and when the API changes, the failure appears far from the cause (a `KeyError` in the reporting step, or worse, wrong numbers with no error at all).

With a contract, you check each record **at the door**, right after extracting it, and you get a precise list of what is wrong: "`amount`: expected str, got float", "`status`: missing". There are two levels of checking:

- **Schema checks** (structure): is every required field present? Is each field the right JSON type? Is `null` allowed here?
- **Data-quality checks** (meaning): is the amount non-negative? Is the status one of the known values? Are ids unique in the batch? Is the newest record recent?

A tiny schema checker needs no library. The schema is a dictionary: field name to `(expected type, nullable)`.

```python
ORDER_SCHEMA = {
    "id": (int, False),
    "customer": (dict, False),
    "status": (str, False),
    "amount": (str, False),
    "currency": (str, False),
    "created_at": (str, False),
    "updated_at": (str, False),
    "items": (list, False),
}
CUSTOMER_SCHEMA = {"email": (str, False), "city": (str, True)}

def check_schema(record, schema, prefix=""):
    """Return a list of error strings; an empty list means the record matches."""
    if not isinstance(record, dict):
        return [f"{prefix or 'record'}: expected object, got {type(record).__name__}"]
    errors = []
    for field, (expected, nullable) in schema.items():
        name = prefix + field
        if field not in record:
            errors.append(f"{name}: missing")
            continue
        value = record[field]
        if value is None:
            if not nullable:
                errors.append(f"{name}: null not allowed")
        elif isinstance(value, bool) and expected is not bool:
            errors.append(f"{name}: expected {expected.__name__}, got bool")
        elif not isinstance(value, expected):
            errors.append(f"{name}: expected {expected.__name__}, got {type(value).__name__}")
    if isinstance(record.get("customer"), dict) and schema is ORDER_SCHEMA:
        errors += check_schema(record["customer"], CUSTOMER_SCHEMA, prefix="customer.")
    return errors
```

The odd-looking `bool` line deals with a Python trap: `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`. Without that line, `{"id": true}` would pass as a valid integer id (Try it 16).

```python
import copy

print(check_schema(ORDERS[0], ORDER_SCHEMA))

bad = copy.deepcopy(ORDERS[0])
bad["id"] = "101"
bad["amount"] = 19.99
del bad["status"]
bad["customer"]["email"] = None
for error in check_schema(bad, ORDER_SCHEMA):
    print(error)
```
```text
[]
id: expected int, got str
status: missing
amount: expected str, got float
customer.email: null not allowed
```

A good order gives an empty list. The bad one gives every problem at once, not just the first, which saves a lot of back-and-forth when you report a broken feed to the API team.

**Unknown extra fields.** The checker ignores fields that are not in the schema. That is deliberate: APIs add fields all the time, and a pipeline that rejects every record because of a new harmless field breaks for no reason. This is called being a **tolerant reader**. Section 15 returns to it.

(In larger projects you would use a validation library such as `pydantic` or `jsonschema`, which do the same thing with more features. Writing a small one yourself first shows you exactly what those libraries check.)

### 6.2 Data-quality checks on one record

After the structure is right, check the meaning. These rules come from the business, not from JSON:

```python
def check_quality(record):
    """Meaning checks for one structurally valid order. Returns a list of error strings."""
    errors = []
    try:
        amount = Decimal(record["amount"])
        if amount < 0:
            errors.append(f"amount: negative ({record['amount']})")
        elif amount > Decimal("100000"):
            errors.append(f"amount: suspiciously large ({record['amount']})")
    except InvalidOperation:
        errors.append(f"amount: not a number ({record['amount']!r})")
    if record["status"] not in STATUSES:
        errors.append(f"status: unknown value {record['status']!r}")
    for field in ("created_at", "updated_at"):
        try:
            parse_ts(record[field])
        except ValueError as error:
            errors.append(f"{field}: {error}")
    if not record["items"]:
        errors.append("items: empty list")
    elif any(not isinstance(i.get("qty"), int) or isinstance(i.get("qty"), bool) or i["qty"] < 1
             for i in record["items"]):
        errors.append("items: qty must be a positive integer")
    return errors

def validate(record):
    """All checks: structure first; meaning only if the structure is right."""
    errors = check_schema(record, ORDER_SCHEMA)
    return errors if errors else check_quality(record)
```

```python
import copy

def variant(**changes):
    record = copy.deepcopy(ORDERS[0])
    record.update(changes)
    return record

samples = [
    ORDERS[0],
    variant(amount="-5.00"),
    variant(amount="N/A", status="lost"),
    variant(created_at="yesterday"),
    variant(updated_at="2024-06-01T12:00:00"),          # no time zone
    variant(items=[]),
    variant(id="104"),                                  # structure error: meaning checks are skipped
]
for record in samples:
    print(record["id"], validate(record))
```
```text
101 []
101 ['amount: negative (-5.00)']
101 ["amount: not a number ('N/A')", "status: unknown value 'lost'"]
101 ["created_at: Invalid isoformat string: 'yesterday'"]
101 ["updated_at: timestamp has no time zone: '2024-06-01T12:00:00'"]
101 ['items: empty list']
104 ['id: expected int, got str']
```

`validate` runs meaning checks only when the structure is right. Running `Decimal(record["amount"])` on a record whose `amount` is missing would raise a `KeyError` inside the checker, which is exactly the kind of crash the checker exists to prevent.

### 6.3 Data-quality checks on a batch

Some problems cannot be seen in one record. They only show up when you look at the whole batch:

- **Null rate**: what fraction of records has `city = null`? 2 percent is normal; 95 percent means the API stopped sending cities.
- **Uniqueness**: does any `id` appear twice in the batch?
- **Volume**: yesterday 10,000 orders, today 12. Is the shop closed, or is the extract broken?
- **Referential integrity**: does every item's `sku` exist in the book catalogue?
- **Freshness**: how old is the newest `updated_at`? If the newest change is three days old, the source may have stopped updating.

A batch report is a plain dictionary of numbers. The time is **injected** (`now`), so the report is repeatable in tests:

```python
from collections import Counter
from datetime import datetime, timezone

CATALOGUE = {"B1", "B2", "B3", "B4"}           # note: no B5

def batch_report(records, now, catalogue):
    n = len(records)
    ids = Counter(r["id"] for r in records)
    city_nulls = sum(1 for r in records if r["customer"]["city"] is None)
    unknown_skus = sorted({i["sku"] for r in records for i in r["items"]} - catalogue)
    newest = max(parse_ts(r["updated_at"]) for r in records)
    return {
        "records": n,
        "duplicate_ids": sorted(i for i, c in ids.items() if c > 1),
        "city_null_rate": round(city_nulls / n, 3),
        "unknown_skus": unknown_skus,
        "newest_update": newest.isoformat(),
        "staleness_hours": round((now - newest).total_seconds() / 3600, 1),
    }

batch = ORDERS + [ORDERS[2]]                     # order 103 delivered twice
now = datetime(2024, 6, 5, 9, 0, tzinfo=timezone.utc)
for key, value in batch_report(batch, now, CATALOGUE).items():
    print(f"{key:16} {value}")
```
```text
records          8
duplicate_ids    [103]
city_null_rate   0.125
unknown_skus     ['B5']
newest_update    2024-06-04T09:00:00+00:00
staleness_hours  24.0
```

The report found the duplicate 103, a city null rate of 1 in 8 (only order 102 has no city), the unknown SKU `B5` (in order 106), and that the newest change is 24 hours old. Whether each finding is a problem is a **threshold** you set: for example "fail the run if `staleness_hours > 48`", "warn if `city_null_rate > 0.2`".

### 6.4 Severity: fail, quarantine, or warn

Not every failed check should stop the pipeline. Decide, for each check, which action fits:

| Finding | Typical action | Reason |
|---|---|---|
| One record has `amount = "N/A"` | **Quarantine** that record, continue | One bad row should not block 10,000 good ones (section 7). |
| 40% of records fail the schema | **Fail** the run | Something changed at the source; loading the 60% would give misleading totals. |
| A duplicate id within one batch | **Fix** (dedupe, section 9) and count it | Common and harmless with a keyed sink. |
| `city_null_rate` rose from 2% to 15% | **Warn** (log, alert) | Suspicious but not certainly wrong. |
| Newest record is 3 days old | **Fail** or alert loudly | Every downstream report would be stale. |
| Unknown SKU in an item | **Warn** or quarantine | Maybe the catalogue sync is late. |

Write these decisions down next to the checks. A check without a decided action is just noise in a log.

### 6.5 Checks in SQL after loading

Some checks are easiest after the data is in the database, where SQL can look at all of it, including data from earlier runs. These are the same queries you wrote in the last chapter, used as **assertions**: each one should return no rows (or zero).

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE orders (id INTEGER, status TEXT, amount_cents INTEGER, city TEXT)")
con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)",
                [(101, "shipped", 1999, "Pune"), (102, "pending", 550, None),
                 (103, "shipped", 4200, "Delhi"), (103, "shipped", 4200, "Delhi"),
                 (104, "lost", -100, "Mumbai")])

CHECKS = {
    "duplicate ids": "SELECT id, COUNT(*) FROM orders GROUP BY id HAVING COUNT(*) > 1",
    "negative amounts": "SELECT id, amount_cents FROM orders WHERE amount_cents < 0",
    "unknown status": "SELECT id, status FROM orders WHERE status NOT IN ('shipped', 'pending', 'cancelled')",
    "null city rate": "SELECT ROUND(AVG(city IS NULL), 2) FROM orders",
}
for name, sql in CHECKS.items():
    print(f"{name:17}", con.execute(sql).fetchall())
```
```text
duplicate ids     [(103, 2)]
negative amounts  [(104, -100)]
unknown status    [(104, 'lost')]
null city rate    [(0.2,)]
```

`AVG(city IS NULL)` is a small trick: `city IS NULL` is 1 or 0, so its average is the null rate. A pipeline can run checks like these at the end of every load and fail (or alert) if the first three return any rows. Of course, the better fix for "duplicate ids" is a `PRIMARY KEY`, so duplicates cannot exist at all; a constraint is a check the database runs for you on every write.

### 6.6 Try it: checks

**Try it 16.** What does `check_schema({**ORDERS[0], "id": True}, ORDER_SCHEMA)` return? What would it return if the `bool` line were removed from `check_schema`, and why?

<details><summary>Answer</summary>

```python
print(check_schema({**ORDERS[0], "id": True}, ORDER_SCHEMA))
print(isinstance(True, int), True + 1)
```
```text
['id: expected int, got bool']
True 2
```

With the `bool` line it reports `id: expected int, got bool`. Without it, the record would pass, because `bool` is a subclass of `int` in Python (`True` behaves like 1). JSON `true` would then be stored as id 1, silently colliding with a real order 1. (`{**ORDERS[0], "id": True}` makes a shallow copy with one field replaced; fine here, since nothing nested is changed.)

</details>

**Try it 17.** Using `batch_report` from section 6.3, what is `staleness_hours` for `ORDERS` alone if `now` is `2024-06-04T21:30:00+05:30`? Work it out by hand first.

<details><summary>Answer</summary>

The newest `updated_at` is order 107's `2024-06-04T09:00:00Z`. The `now` given is 21:30 IST, which is 16:00 UTC. The difference is 7 hours.

```python
now_ist = datetime.fromisoformat("2024-06-04T21:30:00+05:30")
print(batch_report(ORDERS, now_ist, CATALOGUE)["staleness_hours"])
```
```text
7.0
```

Because both datetimes are aware, Python subtracts the real instants, whatever offsets they were written in. With a naive `now`, the subtraction would raise `TypeError`, which is the safe failure.

</details>

**Try it 18.** Which check from this section would catch each problem? (a) The API starts sending `amount` as a JSON number `19.99`. (b) The API sends each order twice. (c) The API's database replica froze two days ago and keeps returning the same old data. (d) A new book `B9` is sold before the catalogue lists it.

<details><summary>Answer</summary>

(a) **Schema check**: `amount: expected str, got float`. (b) **Uniqueness** (batch `duplicate_ids`, or the SQL duplicate check; a primary key with upsert absorbs it). (c) **Freshness**: `staleness_hours` grows past the threshold; volume of new changes also drops to zero. No record-level check can see this, because every record is individually valid. (d) **Referential** check: `unknown_skus` contains `B9`. That one is usually a warning, since the catalogue may simply be late.

</details>

## 7. Bad records and quarantine

### 7.1 Never crash on one bad row, never drop it silently

A pipeline processes thousands of records. Sooner or later one of them is broken: an amount of `"N/A"`, a missing field, a date with no time zone. There are three things you could do, and two of them are wrong:

1. **Crash.** One bad order out of 10,000 stops the run, the 9,999 good ones are not loaded, finance has no report, and the job fails again tomorrow on the same record. Wrong.
2. **Skip silently** (`except: continue`). The run "succeeds", the report is short by one order, and nobody knows. Wrong, and more dangerous than crashing, because it hides the problem.
3. **Quarantine.** Put the bad record aside, **with the reason**, somewhere a human can look; count it; continue with the rest; and report the count in the run summary. Right.

Quarantine is sometimes called a **dead-letter** file or table (from the post office's "dead letter office" for undeliverable mail).

### 7.2 A quarantine file in JSON Lines

**JSON Lines** (`.jsonl`) is a text format with one JSON document per line. It is perfect for quarantine: you can append one line per bad record without reading the file, each line is complete on its own, and a crash in the middle loses at most the last line.

Each quarantine line should carry enough to understand and replay the problem: the reason(s), the original record exactly as received, the run id, and when it was quarantined.

```python
import copy
import json
from pathlib import Path

def quarantine(path, record, reasons, run_id):
    line = {"run_id": run_id, "reasons": reasons, "record": record}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")

def process(records, quarantine_path, run_id):
    good, bad = [], 0
    for record in records:
        errors = validate(record)
        if errors:
            quarantine(quarantine_path, record, errors, run_id)
            bad += 1
            continue
        good.append(flatten_order(record))
    return good, bad

broken = copy.deepcopy(ORDERS[3]); broken["amount"] = "N/A"
no_tz = copy.deepcopy(ORDERS[5]); no_tz["created_at"] = "2024-06-03T16:45:00"
batch = [ORDERS[0], broken, ORDERS[2], no_tz, ORDERS[6]]

qpath = Path("quarantine.jsonl")
good, bad = process(batch, qpath, run_id="run-002")
print("good:", [row["id"] for row in good], "| quarantined:", bad)
for line in qpath.read_text(encoding="utf-8").splitlines():
    entry = json.loads(line)
    print(entry["run_id"], entry["record"]["id"], entry["reasons"])
```
```text
good: [101, 103, 107] | quarantined: 2
run-002 104 ["amount: not a number ('N/A')"]
run-002 106 ["created_at: timestamp has no time zone: '2024-06-03T16:45:00'"]
```

Three good rows went on, two bad ones went aside with readable reasons, and the run did not crash. The original record is kept whole, so after the API team fixes the source (or you fix your parser), the quarantined records can be replayed.

The `timestamp` of quarantining is left out here so the example output is repeatable; a real pipeline adds `"quarantined_at": now.isoformat()` with `now` injected.

**Quarantine can hold personal data.** The quarantined record contains the customer's email. A quarantine file needs the same protection as the main data: limited access, and deletion after a retention period (section 16).

### 7.3 Catch the errors you expect, not every error

`validate` returns a list of problems for every situation it knows. But a transform can still meet something new. The safety net is a `try`/`except` around **each record**, catching the data errors that parsing can raise:

```python
import copy

DATA_ERRORS = (KeyError, TypeError, ValueError, InvalidOperation, AttributeError)

def process_safely(records):
    good, bad = [], []
    for record in records:
        try:
            good.append(flatten_order(record))
        except DATA_ERRORS as error:
            bad.append((record.get("id") if isinstance(record, dict) else None,
                        f"{type(error).__name__}: {error}"))
    return good, bad

r1 = copy.deepcopy(ORDERS[0]); del r1["currency"]
r2 = copy.deepcopy(ORDERS[1]); r2["items"] = [{"sku": "B2", "qty": "one"}]
r3 = copy.deepcopy(ORDERS[2]); r3["status"] = None
r4 = "this is not even a dict"
good, bad = process_safely([r1, r2, r3, r4, ORDERS[4]])
print("good:", [g["id"] for g in good])
for item in bad:
    print(item)
```
```text
good: [105]
(101, "KeyError: 'currency'")
(102, "TypeError: unsupported operand type(s) for +: 'int' and 'str'")
(103, "AttributeError: 'NoneType' object has no attribute 'strip'")
(None, "TypeError: string indices must be integers, not 'str'")
```

Four bad records, three kinds of exception (`KeyError`, `TypeError`, `AttributeError`), all caught and recorded, and the good record still made it through. Look at how unhelpful some of the messages are on their own: "unsupported operand type(s) for +" does not say which field was wrong. That is why `validate` (with its readable reasons) runs first, and this `try`/`except` is only the last safety net. Three points about this pattern:

- **Name the exceptions.** `except Exception` would also catch bugs in your own code, such as a `NameError` from a typo, and quarantine every record "because of bad data" when the real problem is the program. A bug should crash loudly. Catching a known tuple of data errors keeps the two apart.
- **Never a bare `except:`.** It also catches `KeyboardInterrupt` and `SystemExit`, so you cannot even stop the program with Ctrl+C.
- **The try block should be small**: only the per-record work. If the `try` also wraps the database write, a database error (disk full, locked) gets treated as one bad record, and the pipeline happily "quarantines" every record while the real problem is the disk.

### 7.4 Failure thresholds: when bad records mean "stop"

Quarantine is right for **occasional** bad records. But if 60 percent of records suddenly fail, something bigger has happened: the API changed its format, or your parser has a bug. Loading the 40 percent that pass would produce reports that look normal and are badly wrong. In that case the pipeline should **stop** and say why.

A **failure threshold** turns this into a rule: abort the run if the bad fraction is above, say, 5 percent. Two details matter:

1. **Small batches need a minimum count.** One bad record out of 3 is 33 percent; aborting for that is silly. Apply the percentage rule only when the batch is big enough, or allow a fixed number of bad records as well.
2. **Decide what an abort means for the good records.** The safest is: load nothing from this run (do everything in one transaction, or write to staging first), so the sink is not left in a half-loaded state. The quarantine file is still written, because it is the evidence of what went wrong.

```python
class TooManyBadRecords(Exception):
    pass

def check_threshold(total, bad, max_fraction=0.05, min_records=20):
    if total == 0:
        return
    if total >= min_records and bad / total > max_fraction:
        raise TooManyBadRecords(f"{bad} of {total} records failed ({bad / total:.0%}), "
                                f"limit is {max_fraction:.0%}; nothing was loaded")
    if total < min_records and bad > max(1, int(total * max_fraction)):
        raise TooManyBadRecords(f"{bad} of {total} records failed in a small batch")

for total, bad in [(1000, 12), (1000, 80), (3, 1), (3, 2), (0, 0)]:
    try:
        check_threshold(total, bad)
        print(f"{bad:3} of {total:4}: ok, continue")
    except TooManyBadRecords as error:
        print(f"{bad:3} of {total:4}: ABORT -", error)
```
```text
 12 of 1000: ok, continue
 80 of 1000: ABORT - 80 of 1000 records failed (8%), limit is 5%; nothing was loaded
  1 of    3: ok, continue
  2 of    3: ABORT - 2 of 3 records failed in a small batch
  0 of    0: ok, continue
```

The numbers (5 percent, 20 records) are business decisions. Make them parameters with sensible defaults, write them in the configuration, and log them, so someone reading a failed run's log knows which limit fired.

**Where to check.** You can check after the whole batch (simple; needs all records first) or after each page (stops sooner; percentages on small early pages are noisy). A common pattern: check per page with the absolute "small batch" rule, and once more at the end with the percentage rule, before the final commit.

### 7.5 Replaying quarantined records

The quarantine file is not a graveyard; it is a to-do list. After the cause is fixed, the records are fed back through the normal pipeline:

```python
def replay(quarantine_path, fix=None):
    entries = [json.loads(line) for line in quarantine_path.read_text(encoding="utf-8").splitlines()]
    records = [e["record"] for e in entries]
    if fix:
        records = [fix(r) for r in records]
    return records

def fix_missing_tz(record):
    record = copy.deepcopy(record)
    for field in ("created_at", "updated_at"):
        if not record[field].endswith("Z") and "+" not in record[field]:
            record[field] += "Z"                       # the API team confirmed: these are UTC
    return record

retry_path = Path("quarantine-replay.jsonl")
good, bad = process(replay(qpath, fix=fix_missing_tz), retry_path, run_id="replay-001")
print("recovered:", [row["id"] for row in good], "| still bad:", bad)
print(retry_path.read_text(encoding="utf-8").strip())
```
```text
recovered: [106] | still bad: 1
{"reasons": ["amount: not a number ('N/A')"], "record": {"amount": "N/A", "created_at": "2024-06-02T14:00:00Z", "currency": "INR", "customer": {"city": "Mumbai", "email": "dia@example.com"}, "id": 104, "items": [{"qty": 1, "sku": "B4"}], "status": "cancelled", "updated_at": "2024-06-03T08:00:00Z"}, "run_id": "replay-001"}
```

The record with the missing time zone was recovered (after the API team confirmed the times were UTC; never guess a time zone yourself). The `"N/A"` amount is still bad, and it went into a new quarantine file for the replay. Because the sink is keyed and idempotent (section 9), loading recovered records later is safe even if some of them were loaded before.

### 7.6 Try it: bad records

**Try it 19.** For each record, say which exception `flatten_order` raises (it does not call `validate`): (a) `status` is `"Shipped "` (capital S, trailing space); (b) `customer` is `null`; (c) `items` is `null`; (d) `amount` is `19.99` (a float, not a string).

<details><summary>Answer</summary>

```python
for change in [{"status": "Shipped "}, {"customer": None}, {"items": None}, {"amount": 19.99}]:
    record = copy.deepcopy(ORDERS[0]); record.update(change)
    try:
        row = flatten_order(record)
        print(change, "-> ok:", row["status"], row["customer_email"], row["amount"])
    except DATA_ERRORS as error:
        print(change, "->", type(error).__name__, error)
```
```text
{'status': 'Shipped '} -> ok: shipped asha@example.com 19.99
{'customer': None} -> ok: shipped None 19.99
{'items': None} -> TypeError object of type 'NoneType' has no len()
{'amount': 19.99} -> ok: shipped asha@example.com 19.989999999999998436805981327779591083526611328125
```

(a) **No exception**: `flatten_order` strips and lowercases the status, so `"Shipped "` becomes `shipped`. (b) **No exception** either: `order["customer"] or {}` turns `null` into an empty dict, so email and city become `None`. Whether an order without a customer is acceptable is the contract's job, and `check_schema` rejects it (`customer: null not allowed`). (c) `TypeError`, because `len(None)` fails. (d) No exception, and that is a **trap**: `Decimal(19.99)` accepts a float and silently gives 19.989999999999998... (Try it 13). Only the schema check (`amount: expected str, got float`) catches it. This is why validation runs before the transform.

</details>

**Try it 20.** With `check_threshold(total, bad, max_fraction=0.05, min_records=20)`, which of these abort: (a) 50 of 1,000; (b) 51 of 1,000; (c) 1 of 10; (d) 2 of 10; (e) 2 of 50?

<details><summary>Answer</summary>

```python
for total, bad in [(1000, 50), (1000, 51), (10, 1), (10, 2), (50, 2)]:
    try:
        check_threshold(total, bad)
        print(bad, "of", total, "ok")
    except TooManyBadRecords:
        print(bad, "of", total, "ABORT")
```
```text
50 of 1000 ok
51 of 1000 ABORT
1 of 10 ok
2 of 10 ABORT
2 of 50 ok
```

(a) 5.0 percent is not **more** than 5 percent: ok. (b) 5.1 percent: abort. (c) Small batch: allowed is `max(1, int(10 * 0.05)) = max(1, 0) = 1`, and 1 is not more than 1: ok. (d) 2 > 1: abort. (e) 50 records is a big batch; 4 percent: ok. Boundary cases like (a) are exactly where tests should look: decide whether the limit is "more than" or "at least", and test both sides.

</details>

## 8. Incremental loads and watermarks

### 8.1 Full loads and incremental loads

There are two ways to keep a copy of the source up to date.

- **Full load**: every run fetches **everything** and replaces the copy. Simple, and automatically correct: whatever the source says now is what you have. But the cost grows with the size of the data, not with the amount of change. Fetching ten million orders every hour because 300 changed is wasteful, slow, and may break the API's rate limit.
- **Incremental load**: every run fetches only what **changed since the last run**, and merges it into the copy. The cost grows with the amount of change. But now the pipeline must remember where it got to, and must merge correctly.

A good default: full loads for small tables (a few thousand rows, such as the book catalogue), incremental loads for big, growing ones (orders, events). Many teams also run an occasional full load of a big table (weekly, say) to repair anything the incremental runs missed (section 8.7).

### 8.2 The watermark

Incremental loads need the source to say **when each record last changed**. Our API has `updated_at`, and it accepts `updated_since=T` to return only orders changed after `T`. The pipeline remembers the largest `updated_at` it has loaded. That value is the **watermark** (or **high-water mark**, from the line a flood leaves on a wall: the highest point the water reached).

Each run:

1. read the watermark from the state store (nothing on the first run, which means "fetch everything");
2. fetch orders with `updated_since=<watermark>`;
3. upsert them into the sink;
4. set the watermark to the largest `updated_at` among the loaded records, **after** the load has committed.

The state store is a small table in the same database. Keeping state next to the data means one transaction can update both (section 11.5).

```python
import sqlite3

def setup_db(con):
    con.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY, status TEXT NOT NULL, amount_cents INTEGER NOT NULL,
        updated_at TEXT NOT NULL)""")
    con.execute("CREATE TABLE IF NOT EXISTS pipeline_state (name TEXT PRIMARY KEY, value TEXT)")

def get_state(con, name):
    row = con.execute("SELECT value FROM pipeline_state WHERE name = ?", (name,)).fetchone()
    return row[0] if row else None

def set_state(con, name, value):
    con.execute("INSERT INTO pipeline_state (name, value) VALUES (?, ?) "
                "ON CONFLICT(name) DO UPDATE SET value = excluded.value", (name, value))

def upsert_orders(con, records):
    """Insert or update; an update only wins if it is newer. Returns rows written."""
    before = con.total_changes
    con.executemany("""
        INSERT INTO orders (id, status, amount_cents, updated_at) VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            status = excluded.status, amount_cents = excluded.amount_cents,
            updated_at = excluded.updated_at
        WHERE excluded.updated_at > orders.updated_at""",
        [(r["id"], r["status"], int(Decimal(r["amount"]) * 100), r["updated_at"]) for r in records])
    return con.total_changes - before
```

(`con.total_changes` counts the rows changed on this connection so far; the difference before and after tells us how many rows this call really inserted or updated. The `WHERE` on the `DO UPDATE` is explained in section 9.)

```python
def incremental_run(con, client, per_page=3):
    watermark = get_state(con, "orders_watermark")
    params = {"per_page": per_page}
    if watermark is not None:
        params["updated_since"] = watermark
    fetched = written = 0
    newest = watermark
    page = 1
    while page is not None:
        body = client.get("/v1/orders", params={**params, "page": page}).raise_for_status().json()
        with con:
            written += upsert_orders(con, body["data"])
        fetched += len(body["data"])
        for record in body["data"]:
            if newest is None or record["updated_at"] > newest:
                newest = record["updated_at"]
        page = body["next_page"]
    with con:
        if newest is not None:
            set_state(con, "orders_watermark", newest)
    return {"since": watermark, "fetched": fetched, "written": written, "watermark": newest}
```

```python
import copy

server = copy.deepcopy(ORDERS)             # the source data; we will change it between runs
con = sqlite3.connect(":memory:")
setup_db(con)
log = []
client = make_client(server, log=log)

print("run 1:", incremental_run(con, client))
print("run 2:", incremental_run(con, client))
```
```text
run 1: {'since': None, 'fetched': 7, 'written': 7, 'watermark': '2024-06-04T09:00:00Z'}
run 2: {'since': '2024-06-04T09:00:00Z', 'fetched': 0, 'written': 0, 'watermark': '2024-06-04T09:00:00Z'}
```

Run 1 had no watermark, fetched all seven orders and set the watermark to order 107's `updated_at`. Run 2 asked only for changes after that time, got nothing, and wrote nothing. Now the source changes: the customer cancels order 105, and a new order 108 arrives.

```python
server[4]["status"] = "cancelled"
server[4]["updated_at"] = "2024-06-04T10:00:00Z"
server.append({**copy.deepcopy(ORDERS[0]), "id": 108, "amount": "8.00",
               "created_at": "2024-06-04T10:30:00Z", "updated_at": "2024-06-04T10:30:00Z"})

log.clear()
print("run 3:", incremental_run(con, client))
print("request:", log)
print(con.execute("SELECT id, status, updated_at FROM orders WHERE id IN (105, 108)").fetchall())
print("rows in table:", con.execute("SELECT COUNT(*) FROM orders").fetchone()[0])
```
```text
run 3: {'since': '2024-06-04T09:00:00Z', 'fetched': 2, 'written': 2, 'watermark': '2024-06-04T10:30:00Z'}
request: [{'per_page': '3', 'updated_since': '2024-06-04T09:00:00Z', 'page': '1'}]
[(105, 'cancelled', '2024-06-04T10:00:00Z'), (108, 'shipped', '2024-06-04T10:30:00Z')]
rows in table: 8
```

Run 3 fetched exactly the two changed orders with one request, updated 105 in place, inserted 108, and moved the watermark forward. The table has eight rows: no duplicates, nothing missing.

### 8.3 `>` or `>=`: the equal-timestamp problem

Look closely at the API contract: `updated_since=T` returns records with `updated_at > T`, **strictly greater**. That looks natural, since we already have the record at exactly `T`. It hides a nasty bug.

Timestamps have limited precision (here, whole seconds). Several records can share the same `updated_at`. Suppose two orders are both updated at `09:00:00`, but the second one is **saved** on the server a few milliseconds after our run read the first. Our run sees only the first, sets the watermark to `09:00:00`, and the next run asks for `updated_at > 09:00:00`. The second order, stamped exactly `09:00:00`, is never returned. **It is lost for good**, and no error is ever raised.

Here it is for real. Run 1 sees orders 101 to 107; the watermark becomes 107's `09:00:00`. Then order 109 appears with the same `updated_at`:

```python
import copy

def two_runs(inclusive):
    server = copy.deepcopy(ORDERS)
    con = sqlite3.connect(":memory:")
    setup_db(con)
    client = make_client(server, inclusive=inclusive)
    first = incremental_run(con, client)
    server.append({**copy.deepcopy(ORDERS[0]), "id": 109,
                   "updated_at": "2024-06-04T09:00:00Z"})      # same second as order 107
    second = incremental_run(con, client)
    ids = [row[0] for row in con.execute("SELECT id FROM orders ORDER BY id")]
    return first, second, ids

for inclusive in (False, True):
    first, second, ids = two_runs(inclusive)
    op = ">=" if inclusive else "> "
    print(f"API uses {op}: run 2 fetched={second['fetched']} written={second['written']} | 109 loaded: {109 in ids}")
```
```text
API uses > : run 2 fetched=0 written=0 | 109 loaded: False
API uses >=: run 2 fetched=2 written=1 | 109 loaded: True
```

With `>`, run 2 fetched nothing and order 109 is missing forever. With `>=`, run 2 fetched **two** records: order 107 again (it has exactly the watermark time) and the new 109. Order 107 was fetched twice in total, but the "only if newer" upsert wrote nothing for it the second time, so the table is still correct, and 109 is there.

The lesson, which you should remember as a rule:

> **Re-fetching a record is harmless if the sink is idempotent. Missing a record is a silent, permanent error.** So always choose the option that may fetch too much (`>=`, an overlap window) and make the sink absorb duplicates.

If the API only offers `>`, you can still get the same safety by asking for a slightly earlier time than your watermark: the overlap window in the next section.

A second fix, when the API supports it, is a **compound watermark**: remember `(updated_at, id)` of the last record and ask for records "after this pair" in the same sort order. That is exactly what a cursor does, which is one more reason cursors are pleasant.

### 8.4 Late data and the overlap window

Equal timestamps are one case of a wider problem: **late data**, records that arrive in the API **after** records with later timestamps. It happens all the time in real systems:

- the API reads from a database **replica** that is a few seconds behind;
- the record's timestamp was set by a different machine whose clock is a little off (**clock skew**);
- a long transaction set `updated_at` when it started but committed a minute later.

In each case, a record with `updated_at = 08:59:50` can appear in the API after your run has already moved the watermark to `09:00:00`. With `updated_since = watermark`, it is never fetched.

The standard defence is an **overlap window** (or **lookback**): ask for changes since `watermark - overlap`, for example ten minutes before the watermark. Every run re-reads the last ten minutes. Records that arrived late, within that window, are caught. Records that were already loaded are fetched again and absorbed by the idempotent upsert.

```python
import copy
from datetime import timedelta

def since_with_overlap(watermark, overlap=timedelta(minutes=10)):
    if watermark is None:
        return None
    return (parse_ts(watermark) - overlap).strftime("%Y-%m-%dT%H:%M:%SZ")

print(since_with_overlap("2024-06-04T09:00:00Z"))

def run_with_overlap(con, client, overlap):
    watermark = get_state(con, "orders_watermark")
    params = {"per_page": 100}
    since = since_with_overlap(watermark, overlap)
    if since is not None:
        params["updated_since"] = since
    records = client.get("/v1/orders", params=params).raise_for_status().json()["data"]
    with con:
        written = upsert_orders(con, records)
        if records:
            newest = max([r["updated_at"] for r in records] + ([watermark] if watermark else []))
            set_state(con, "orders_watermark", newest)
    return len(records), written

for overlap in (timedelta(0), timedelta(minutes=10)):
    server = copy.deepcopy(ORDERS)
    con = sqlite3.connect(":memory:")
    setup_db(con)
    client = make_client(server)
    run_with_overlap(con, client, overlap)
    server.append({**copy.deepcopy(ORDERS[0]), "id": 110,
                   "updated_at": "2024-06-04T08:55:00Z"})      # 5 minutes BEFORE the watermark, but late
    fetched, written = run_with_overlap(con, client, overlap)
    found = con.execute("SELECT COUNT(*) FROM orders WHERE id = 110").fetchone()[0]
    print(f"overlap {overlap}: run 2 fetched {fetched}, wrote {written}, order 110 loaded: {bool(found)}")
```
```text
2024-06-04T08:50:00Z
overlap 0:00:00: run 2 fetched 0, wrote 0, order 110 loaded: False
overlap 0:10:00: run 2 fetched 2, wrote 1, order 110 loaded: True
```

(One detail in `run_with_overlap`: the new watermark is the maximum of the old watermark and the records' times. Without the old one in the `max`, a run that only re-fetched older, overlapping records could move the watermark **backwards**.)

How long should the overlap be? Long enough to cover the worst lateness you have seen, with a margin: minutes for replica lag, hours if a source is known to batch its writes. The cost is re-fetching that window on every run, which is usually small. If records can be **very** late (days), no overlap is enough, and you add a periodic full reconcile.

### 8.5 When, and from what, to move the watermark

Two rules decide whether incremental loads are trustworthy.

**Rule 1: move the watermark only after the data is safely written.** If the watermark is saved first and the program crashes before the data is committed, the next run starts after data that was never loaded. That data is lost. Data first, watermark second (or both in one transaction).

**Rule 2: take the watermark from the data, not from the clock.** It is tempting to set `watermark = now()` at the start or end of a run. But "now" on your machine is not "now" on the source. If your clock is two minutes ahead of the server's, records stamped in those two minutes are skipped. If a record is committed late (section 8.4), it is skipped. The largest `updated_at` you actually **received** is a fact about the source; your clock is not.

A third, smaller rule: **if a run fetched nothing, do not change the watermark.** There is no new evidence.

### 8.6 Incremental loads need an idempotent sink

Put sections 8.3 and 8.4 together and a pattern appears. To be safe, an incremental pipeline deliberately fetches some records more than once (inclusive comparison, overlap window, retries, resumes). That is only acceptable if writing the same record twice has the same effect as writing it once. So **incremental loading and idempotent writing are two halves of one design**. The next section is about the second half.

### 8.7 Deletes: what incremental loads cannot see

If an order is **deleted** at the source, it does not appear in "orders changed since T", because it no longer exists. An incremental pipeline never learns about it, and the copy keeps the order forever. Three ways to deal with this:

1. **Soft deletes**: the source never really deletes; it sets `status = "deleted"` or `deleted_at = ...` and bumps `updated_at`. Then the deletion is just another change. This is the best option, and worth asking the API team for.
2. **A deletions feed**: some APIs offer `GET /v1/orders/deleted?since=T`.
3. **Periodic full reconcile**: once a week, fetch all ids from the source and delete (or mark) the ones your copy has but the source does not. This also repairs anything else the incremental runs missed.

### 8.8 Try it: incremental loads

**Try it 21.** Trace this by hand, then check. The API uses `>`, the watermark starts empty, and runs happen in this order:

1. Run A. The source holds orders 101 to 103 (from `ORDERS`).
2. Order 104 (`updated_at` `2024-06-03T08:00:00Z`) and order 111 with `updated_at` `2024-06-02T09:15:00Z` (exactly order 103's time) are added.
3. Run B.

What watermark does each run leave, and which of 104 and 111 are loaded? Then: what would change with an API that uses `>=`?

<details><summary>Answer</summary>

```python
import copy

def trace(inclusive):
    server = copy.deepcopy(ORDERS[:3])
    con = sqlite3.connect(":memory:")
    setup_db(con)
    client = make_client(server, inclusive=inclusive)
    a = incremental_run(con, client)
    server.append(copy.deepcopy(ORDERS[3]))
    server.append({**copy.deepcopy(ORDERS[0]), "id": 111, "updated_at": "2024-06-02T09:15:00Z"})
    b = incremental_run(con, client)
    ids = {r[0] for r in con.execute("SELECT id FROM orders")}
    return a["watermark"], b["watermark"], b["fetched"], 104 in ids, 111 in ids

print(">  :", trace(False))
print(">= :", trace(True))
```
```text
>  : ('2024-06-02T09:15:00Z', '2024-06-03T08:00:00Z', 1, True, False)
>= : ('2024-06-02T09:15:00Z', '2024-06-03T08:00:00Z', 3, True, True)
```

Run A leaves `2024-06-02T09:15:00Z` (order 103). Run B asks for `updated_at > 09:15:00` on 2 June and gets only 104, so the watermark moves to `2024-06-03T08:00:00Z`. Order 111, stamped exactly at the old watermark, is **lost**. With `>=`, run B re-fetches 103 (harmless), 111 and 104: three records, nothing lost.

</details>

**Try it 22.** A teammate suggests: "Instead of tracking the max `updated_at`, just save `datetime.now(timezone.utc)` at the start of each run, and ask for `updated_since=<last start time>` next time. It is simpler." Give two ways this loses data.

<details><summary>Answer</summary>

1. **Clock differences**: your machine's clock and the source's clock are not the same. If yours runs ahead, records the source stamps in the gap (by its clock, before your "now") are created after your run started but are older than your saved time, so they are never fetched.
2. **Late commits and replica lag**: a record stamped `10:00:00` may only become visible in the API at `10:00:05`. A run that started at `10:00:02` did not see it, and the next run asks for `> 10:00:02`. Lost.

Taking the watermark from the data you actually received avoids the first problem completely and, combined with an overlap window, handles the second.

</details>

## 9. Deduplication and idempotent writes

### 9.1 Where duplicates come from

In a pipeline, duplicates are not a rare accident; the safe designs **create** them on purpose:

- **Overlap windows and `>=`** re-fetch recent records (section 8).
- **Retries** re-send a request whose response was lost, so a page arrives twice (section 10).
- **Resumes** redo the page that was in progress when the run crashed (section 11).
- **Offset pagination** returns a record on two pages when data shifts (section 3.8).
- **The source itself** sometimes sends the same event twice.
- **People** run the job again "to be sure".

So the question is never "how do I avoid duplicates?" but "how do I make them harmless?". Two tools: **dedupe within a batch** in Python, and **idempotent writes** in the sink.

### 9.2 Deduplicating a batch: keep the latest version

Within one batch, the same id can appear more than once, possibly with different versions. Keep one record per id: the one with the latest `updated_at`. When two copies have the **same** `updated_at`, we need a tie rule; a common choice is "the one seen last wins", because later pages are usually newer reads.

```python
def dedupe_latest(records):
    best = {}
    for record in records:
        current = best.get(record["id"])
        if current is None or record["updated_at"] >= current["updated_at"]:   # >= : ties go to the later one
            best[record["id"]] = record
    return list(best.values())

batch = [
    {"id": 1, "status": "pending", "updated_at": "2024-06-01T10:00:00Z"},
    {"id": 2, "status": "pending", "updated_at": "2024-06-01T10:05:00Z"},
    {"id": 1, "status": "shipped", "updated_at": "2024-06-01T12:00:00Z"},   # newer version of 1
    {"id": 2, "status": "cancelled", "updated_at": "2024-06-01T09:00:00Z"}, # OLDER version of 2 arrives late
    {"id": 3, "status": "pending", "updated_at": "2024-06-01T11:00:00Z"},
    {"id": 3, "status": "shipped", "updated_at": "2024-06-01T11:00:00Z"},   # same time: tie
]
for record in dedupe_latest(batch):
    print(record)
```
```text
{'id': 1, 'status': 'shipped', 'updated_at': '2024-06-01T12:00:00Z'}
{'id': 2, 'status': 'pending', 'updated_at': '2024-06-01T10:05:00Z'}
{'id': 3, 'status': 'shipped', 'updated_at': '2024-06-01T11:00:00Z'}
```

Order 1 kept its newer `shipped` version. Order 2 kept `pending`, because the `cancelled` copy is **older** even though it came later in the list; "last one wins" without looking at `updated_at` would have gone back in time. Order 3 was a tie, and the later copy won. The dictionary keeps the order in which each id was **first** seen, which is why the output is 1, 2, 3.

(Comparing `updated_at` as text works here only because every value has the same format and time zone. In a real pipeline, compare parsed datetimes, or normalise the text to one UTC format first, as section 5.3 recommends.)

### 9.3 Keys: what makes a record "the same"

Deduplication and upserts both need a **key**: the field or fields that identify a record.

- A **natural key** comes from the data itself: the order id from the source system, an ISBN, an email address. Pipelines should use the **source's** id as the key, because it is what stays the same when the same record arrives twice.
- A **surrogate key** is invented by your database, such as an `INTEGER PRIMARY KEY` that counts 1, 2, 3. It is useful inside your database, but it cannot detect duplicates from outside: the second copy of order 101 just gets the next number.
- A **composite key** uses several fields: an order line is identified by `(order_id, line_number)` or `(order_id, sku)`; a daily total by `(day, city)`.

Before writing any load, finish this sentence: "two records are the same record when ___ are equal". If you cannot finish it, the load cannot be idempotent.

Be careful with keys that are not really stable. Email addresses change. Names are not unique. A key built from "every field" means any changed value creates a new row instead of updating the old one.

### 9.4 UPSERT, only if newer

You know UPSERT from the last chapter. For pipelines, plain UPSERT has a problem: it always overwrites. If an **older** version arrives after a newer one (late data, a replay of quarantined records, an out-of-order retry), plain UPSERT goes back in time. The fix is a `WHERE` on the update part: update only if the incoming version is newer.

```python
con = sqlite3.connect(":memory:")
setup_db(con)

def show(con):
    for row in con.execute("SELECT id, status, updated_at FROM orders ORDER BY id"):
        print("   ", row)

def load(label, records):
    with con:
        written = upsert_orders(con, records)
    print(f"{label}: wrote {written}")

v1 = {"id": 101, "status": "pending", "amount": "19.99", "updated_at": "2024-06-01T10:00:00Z"}
v2 = {**v1, "status": "shipped", "updated_at": "2024-06-01T12:00:00Z"}

load("new v1         ", [v1])
load("newer v2       ", [v2])
load("old v1 again   ", [v1])          # a late replay of the old version
load("same v2 again  ", [v2])          # a duplicate of the current version
show(con)
```
```text
new v1         : wrote 1
newer v2       : wrote 1
old v1 again   : wrote 0
same v2 again  : wrote 0
    (101, 'shipped', '2024-06-01T12:00:00Z')
```

The late `v1` and the duplicate `v2` both wrote **zero** rows, and the table holds the newest version. This upsert is idempotent (re-applying the same record changes nothing) and **order-independent** (old versions cannot overwrite new ones). Those two properties together are what let the rest of the pipeline fetch generously.

Here is the statement on its own, for reference:

```sql
INSERT INTO orders (id, status, amount_cents, updated_at) VALUES (?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    status = excluded.status,
    amount_cents = excluded.amount_cents,
    updated_at = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
```

`excluded` is the row you tried to insert; `orders` is the row already there. Use `>` here, not `>=`: an equal timestamp means the same version, so there is nothing to update. (If the source can change a record **without** changing `updated_at`, then you need `>=`, or a comparison of the values. Find out how your source behaves.)

### 9.5 The `INSERT OR REPLACE` trap

SQLite also has `INSERT OR REPLACE` (and MySQL has `REPLACE INTO`). It looks like an upsert, but it is not: on a conflict it **deletes** the old row and **inserts** a new one. Any column you did not supply is reset to its default, and any foreign keys or triggers on delete fire.

```python
con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT,
               first_seen_run TEXT DEFAULT NULL)""")
con.execute("INSERT INTO orders VALUES (101, 'pending', 'run-001')")

con.execute("INSERT OR REPLACE INTO orders (id, status) VALUES (101, 'shipped')")
print("OR REPLACE:", con.execute("SELECT * FROM orders").fetchall())

con.execute("UPDATE orders SET first_seen_run = 'run-001' WHERE id = 101")
con.execute("INSERT INTO orders (id, status) VALUES (101, 'cancelled') "
            "ON CONFLICT(id) DO UPDATE SET status = excluded.status")
print("UPSERT:    ", con.execute("SELECT * FROM orders").fetchall())
```
```text
OR REPLACE: [(101, 'shipped', None)]
UPSERT:     [(101, 'cancelled', 'run-001')]
```

`INSERT OR REPLACE` wiped `first_seen_run`, because the "replacement" row did not mention it. The real UPSERT changed only the column it was told to. Prefer `ON CONFLICT ... DO UPDATE`.

### 9.6 Delete and insert per partition

UPSERT works record by record. Some outputs are not records from the source but **results you compute**, such as daily revenue per city. If the input for 3 June changes (an order is cancelled), the old total for 3 June is wrong, and maybe a city that had revenue now has none, so its row should disappear. Upserting the new rows does not remove the old row.

For computed outputs the idempotent pattern is **delete and insert per partition, in one transaction**: for each day being processed, delete every row for that day, then insert the freshly computed rows for that day. Because both happen inside one transaction, readers never see the day empty, and a crash in the middle rolls back to the old rows.

```python
import copy

def build_daily_revenue(con, orders, days):
    """Recompute daily_revenue for the given days from scratch. Idempotent per day."""
    rows = {}
    for o in orders:
        flat = flatten_order(o)
        if flat["order_date"] in days and flat["status"] != "cancelled":
            key = (flat["order_date"], flat["customer_city"] or "unknown")
            rows[key] = rows.get(key, 0) + int(flat["amount"] * 100)
    with con:                                                   # one transaction for all days
        for day in days:
            con.execute("DELETE FROM daily_revenue WHERE day = ?", (day,))
        con.executemany("INSERT INTO daily_revenue (day, city, revenue_cents) VALUES (?, ?, ?)",
                        [(day, city, cents) for (day, city), cents in sorted(rows.items())])

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE daily_revenue (day TEXT, city TEXT, revenue_cents INTEGER, PRIMARY KEY (day, city))")
source = copy.deepcopy(ORDERS)
all_days = sorted({flatten_order(o)["order_date"] for o in source})

build_daily_revenue(con, source, all_days)
before = con.execute("SELECT * FROM daily_revenue ORDER BY day, city").fetchall()
for row in before:
    print(row)

build_daily_revenue(con, source, all_days)                     # run it again
print("re-run identical:", con.execute("SELECT * FROM daily_revenue ORDER BY day, city").fetchall() == before)
```
```text
('2024-06-01', 'Pune', 1999)
('2024-06-01', 'unknown', 550)
('2024-06-02', 'Delhi', 4200)
('2024-06-03', 'Chennai', 3000)
('2024-06-03', 'Pune', 775)
('2024-06-04', 'Pune', 1500)
re-run identical: True
```

Now order 105 (Pune, 3 June) is cancelled at the source. Only 3 June needs recomputing:

```python
source[4]["status"] = "cancelled"
build_daily_revenue(con, source, ["2024-06-03"])
for row in con.execute("SELECT * FROM daily_revenue WHERE day = '2024-06-03'"):
    print(row)
print("other days untouched:",
      con.execute("SELECT * FROM daily_revenue WHERE day <> '2024-06-03' ORDER BY day, city").fetchall()
      == [r for r in before if r[0] != "2024-06-03"])
```
```text
('2024-06-03', 'Chennai', 3000)
other days untouched: True
```

The Pune row for 3 June disappeared completely. An upsert could never have done that, because there was no new Pune row to upsert. Days that were not in the list were not touched. This same pattern, "replace the whole partition", appears again for Parquet folders in section 14, and it is how **backfills** work: to repair a month, re-run the pipeline for each day of that month; each day is replaced, and running the backfill twice gives the same table.

### 9.7 Testing "run twice = same result"

Idempotency is easy to claim and easy to test. The test is always the same shape: run the pipeline, take a snapshot of the sink, run it again with the same input, and compare.

```python
def snapshot(con):
    return {
        "orders": con.execute("SELECT * FROM orders ORDER BY id").fetchall(),
        "state": con.execute("SELECT * FROM pipeline_state ORDER BY name").fetchall(),
    }

run_pipeline(con, client)
first = snapshot(con)
run_pipeline(con, client)
assert snapshot(con) == first, "second run changed the data: some write is not idempotent"
```

Include **every** table the pipeline writes, including state and run logs, and decide which differences are allowed. A `runs` table that gets a new row per run is expected to differ; the `orders` table is not.

### 9.8 At-least-once delivery plus an idempotent sink

Distributed systems people use three phrases for how often a message is delivered:

- **At most once**: each record is delivered zero or one times. Simple, and it loses data when something fails.
- **At least once**: each record is delivered one or more times. Retries, overlaps and resumes give you this. Nothing is lost, but duplicates happen.
- **Exactly once**: each record is delivered exactly one time. Over an unreliable network, this is impossible to guarantee for delivery itself.

What pipelines actually build is **at-least-once delivery into an idempotent sink**. Each record may arrive several times, but because the write is keyed and "only if newer", the **effect** is as if it arrived once. People call this "effectively once". When someone asks "is the pipeline exactly-once?", the honest answer is: "delivery is at-least-once; the writes are idempotent, so the result is the same".

### 9.9 Try it: dedupe and idempotent writes

**Try it 23.** Using `upsert_orders` (only if newer), the table holds order 101 with `updated_at` `2024-06-01T12:00:00Z`. Predict how many rows each call writes, and the final status: (a) a version with status `cancelled` and `updated_at` `2024-06-01T11:00:00Z`; (b) a version with status `cancelled` and the **same** `updated_at` 12:00; (c) a version with status `cancelled` and `updated_at` 13:00; (d) (c) again.

<details><summary>Answer</summary>

```python
con = sqlite3.connect(":memory:")
setup_db(con)
with con:
    upsert_orders(con, [v2])
for t in ["2024-06-01T11:00:00Z", "2024-06-01T12:00:00Z", "2024-06-01T13:00:00Z", "2024-06-01T13:00:00Z"]:
    with con:
        n = upsert_orders(con, [{**v2, "status": "cancelled", "updated_at": t}])
    print(t, "wrote", n, "->", con.execute("SELECT status FROM orders").fetchone()[0])
```
```text
2024-06-01T11:00:00Z wrote 0 -> shipped
2024-06-01T12:00:00Z wrote 0 -> shipped
2024-06-01T13:00:00Z wrote 1 -> cancelled
2024-06-01T13:00:00Z wrote 0 -> cancelled
```

(a) 0, older; (b) 0, equal is not newer, even though the status differs, which is why you must know whether your source always bumps `updated_at` on a change; (c) 1, newer, status becomes `cancelled`; (d) 0, same version again.

</details>

**Try it 24.** A pipeline appends each day's orders to a CSV file `orders.csv`. Someone re-runs yesterday's job. What happens, and how would you make the file output idempotent?

<details><summary>Answer</summary>

Yesterday's orders are appended a second time, so the file now contains them twice, and any total computed from it is too high. Appending is not idempotent. Fixes, from simplest: write **one file per day** (`orders_2024-06-03.csv`) and **overwrite** it on each run, which is "replace the partition" for files (section 14); or rebuild the whole file from the database each time. Either way, write to a temporary file first and rename it into place, so a crash never leaves half a file (section 11.2).

</details>

## 10. Retries

### 10.1 Transient and permanent failures

Networks fail. Servers restart. Rate limits kick in. A pipeline that gives up at the first failed request fails every few nights for no real reason; a pipeline that retries everything forever hammers a broken server and never reports the real problem. The skill is telling the two kinds of failure apart.

A **transient** failure goes away if you wait. A **permanent** failure does not.

| Failure | Kind | Retry? |
|---|---|---|
| `httpx.ConnectError`, `httpx.ReadTimeout`, other `TransportError` | transient (usually) | yes |
| 429 Too Many Requests | transient: you are too fast | yes, after the wait the server asks for |
| 500, 502, 503, 504 | transient (usually) | yes |
| 400 Bad Request, 422 Unprocessable | permanent: your request is wrong | no |
| 401 Unauthorized, 403 Forbidden | permanent until a human fixes credentials | no |
| 404 Not Found | permanent (wrong URL, or gone) | no |
| JSON that does not parse on a 200 | unclear: maybe a proxy page | maybe once or twice, then fail |

Retrying a 400 is pointless: the same wrong request gets the same answer. Retrying a 401 is worse: many systems lock an account after repeated failed logins.

### 10.2 Exponential backoff

If a server is struggling, retrying immediately adds load at the worst moment. The standard answer is **exponential backoff**: wait a little after the first failure, twice as long after the second, twice again after the third, up to a cap.

```text
delay(attempt) = min(cap, base * 2 ** attempt)        attempt = 0, 1, 2, ...
base = 1 s, cap = 30 s:   1, 2, 4, 8, 16, 30, 30, ...
```

Exponential growth means a few quick retries handle short blips, while a long outage quickly backs off to one try every 30 seconds instead of hundreds per second.

### 10.3 Jitter

Now imagine 500 copies of a pipeline (or 500 users of one API) that all failed at the same moment, because the server restarted. With plain backoff they all retry after exactly 1 s, then exactly 2 s, then exactly 4 s: synchronized waves of traffic that knock the server over again. This is the **thundering herd**.

**Jitter** adds randomness to spread them out. This chapter (and its problems) uses **equal jitter**: keep half of the backoff delay fixed, and make the other half random.

```text
backoff = min(max_delay, base * 2 ** attempt)
delay   = backoff / 2 + rand() * backoff / 2          rand() is between 0 and 1
```

So the delay is always between half the backoff and the full backoff. The fixed half guarantees that the waits still grow exponentially (a client never retries almost at once); the random half spreads the clients apart.

```python
import random

def backoff(attempt, base=1.0, max_delay=30.0):
    return min(max_delay, base * 2 ** attempt)

def equal_jitter(attempt, rand, base=1.0, max_delay=30.0):
    b = backoff(attempt, base, max_delay)
    return b / 2 + rand() * b / 2

def full_jitter(attempt, rand, base=1.0, max_delay=30.0):
    return rand() * backoff(attempt, base, max_delay)

print("plain:       ", [backoff(a) for a in range(7)])
rng = random.Random(7)                     # a seeded generator: the same "random" numbers every time
print("equal jitter:", [round(equal_jitter(a, rng.random), 2) for a in range(7)])
print("rand()=1.0:  ", [equal_jitter(a, lambda: 1.0) for a in range(7)])
print("rand()=0.0:  ", [equal_jitter(a, lambda: 0.0) for a in range(7)])
```
```text
plain:        [1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0]
equal jitter: [0.66, 1.15, 3.3, 4.29, 12.29, 20.49, 15.87]
rand()=1.0:   [1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0]
rand()=0.0:   [0.5, 1.0, 2.0, 4.0, 8.0, 15.0, 15.0]
```

The plain delays are the same for every client in the world; the jittered ones are different for each client (here they are repeatable only because we seeded the generator so the example prints the same thing every time). With `rand()` at its extremes you can see the range: `1.0` gives exactly the plain backoff, `0.0` gives exactly half of it.

A common alternative is **full jitter**, `rand() * backoff`: a random wait anywhere between 0 and the backoff. It spreads clients even more widely, but a client can be unlucky and retry almost immediately. Both are fine; what matters is that **some** jitter is there, and that you know which formula your code (and its tests) use.

Notice the functions take `rand` as an argument instead of calling `random.random()` inside. That is the "inject the randomness" pattern: tests pass `rand=lambda: 1.0` (delays equal the plain backoff) or `rand=lambda: 0.0` (exactly half), and can assert the exact delays.

### 10.4 Honouring `Retry-After`

A 429 or 503 response often includes a `Retry-After` header that says how long to wait: either a number of **seconds** (`Retry-After: 30`) or an HTTP date (`Retry-After: Wed, 05 Jun 2024 10:00:00 GMT`). When the server tells you, obey it: it knows its own rate-limit window. Waiting less gets you another 429; waiting much more wastes time.

```python
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

def retry_after_seconds(response, now):
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    if value.strip().isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None                                   # unreadable: fall back to normal backoff
    return max(0.0, (when - now).total_seconds())

import httpx
now = datetime(2024, 6, 5, 9, 59, 30, tzinfo=timezone.utc)
for header in ["7", "Wed, 05 Jun 2024 10:00:00 GMT", "soon"]:
    print(repr(header), "->", retry_after_seconds(httpx.Response(429, headers={"Retry-After": header}), now))
```
```text
'7' -> 7.0
'Wed, 05 Jun 2024 10:00:00 GMT' -> 30.0
'soon' -> None
```

Use the `Retry-After` value **exactly**, with no jitter added: the server named a time, and the clients are already spread out by when their own requests arrived. But **cap** it at the same `max_delay` as the backoff: if a server says `Retry-After: 86400` (a day), the pipeline should not sleep for a day. Waiting `max_delay` and trying again (and eventually running out of attempts, with a clear error) is safer. Some pipelines instead fail the run at once when the server asks for a very long wait; either way, never sleep for an unbounded time because a header said so.

### 10.5 `call_with_retry`

Here is a retry helper that puts all of this together. Read it slowly; each line is a decision from the sections above. Time and randomness are **injected** (`sleep`, `rand`), so tests run instantly and can check every delay.

```python
import logging
import random
import time

RETRY_STATUS = {429, 500, 502, 503, 504}

def backoff_delay(attempt, base, max_delay, rand):
    """Exponential backoff with equal jitter: between half and all of min(max_delay, base * 2**attempt)."""
    backoff = min(max_delay, base * 2 ** attempt)
    return backoff / 2 + rand() * backoff / 2

def call_with_retry(send, *, max_attempts=5, base=0.5, max_delay=30.0,
                    sleep=time.sleep, rand=random.random, logger=logging.getLogger("pipeline")):
    """Call send() (which returns an httpx.Response) until it succeeds or a permanent error occurs.

    Retries transport errors and 429/5xx. Never retries other 4xx. Raises the last error when
    attempts run out.
    """
    for attempt in range(max_attempts):
        last = attempt == max_attempts - 1
        try:
            response = send()
        except httpx.TransportError as error:
            if last:
                raise
            delay = backoff_delay(attempt, base, max_delay, rand)
            logger.warning("attempt %d failed: %s; retrying in %.2fs", attempt + 1, type(error).__name__, delay)
            sleep(delay)
            continue
        if response.status_code not in RETRY_STATUS:
            return response.raise_for_status()      # success, or a permanent error raised now
        if last:
            response.raise_for_status()
        header = response.headers.get("Retry-After", "").strip()
        if header.isdigit():
            delay = min(float(header), max_delay)   # the server's wait, exactly; no jitter; capped
        else:
            delay = backoff_delay(attempt, base, max_delay, rand)
        logger.warning("attempt %d got %d; retrying in %.2fs", attempt + 1, response.status_code, delay)
        sleep(delay)
```

A **scripted** mock server makes the behaviour visible. It answers from a list, one item per call: a status code, a `(status, headers)` pair, or an exception class to raise.

```python
def scripted_client(*answers):
    """A client whose server replies with answers[0], answers[1], ... (the last one repeats)."""
    calls = []

    def handler(request):
        answer = answers[min(len(calls), len(answers) - 1)]
        calls.append(answer)
        if isinstance(answer, type) and issubclass(answer, Exception):
            raise answer("simulated failure", request=request)
        status, headers = answer if isinstance(answer, tuple) else (answer, {})
        return httpx.Response(status, json={"status": status}, headers=headers)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.pagebound.test")
    return client, calls

class FakeSleep:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)
```

```python
import logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

client, calls = scripted_client(503, (429, {"Retry-After": "7"}), httpx.ConnectError, 200)
sleep = FakeSleep()
response = call_with_retry(lambda: client.get("/v1/orders"), sleep=sleep, rand=lambda: 1.0)
print("result:", response.status_code, "| calls:", len(calls), "| slept:", sleep.delays)
```
```text
WARNING pipeline: attempt 1 got 503; retrying in 0.50s
WARNING pipeline: attempt 2 got 429; retrying in 7.00s
WARNING pipeline: attempt 3 failed: ConnectError; retrying in 2.00s
result: 200 | calls: 4 | slept: [0.5, 7.0, 2.0]
```

Four calls: 503 (wait `0.5 * 2**0 = 0.5`), 429 (the server said 7 seconds, so exactly 7, not the 1.0 the backoff would give), a connection error (wait `0.5 * 2**2 = 2.0`), then success. With `rand=lambda: 1.0` equal jitter gives `backoff/2 + backoff/2`, the full backoff, so the delays are the plain backoff values, which makes them easy to check. A `Retry-After` larger than `max_delay` is cut down to it:

```python
client, calls = scripted_client((429, {"Retry-After": "600"}), 200)
sleep = FakeSleep()
call_with_retry(lambda: client.get("/v1/orders"), max_delay=30.0, sleep=sleep, rand=lambda: 1.0)
print("slept:", sleep.delays)
```
```text
WARNING pipeline: attempt 1 got 429; retrying in 30.00s
slept: [30.0]
```

 Nothing actually slept: `FakeSleep` just wrote the numbers down, so the example ran instantly.

Permanent errors are not retried:

```python
client, calls = scripted_client(404)
sleep = FakeSleep()
try:
    call_with_retry(lambda: client.get("/v1/ordrs"), sleep=sleep)
except httpx.HTTPStatusError as error:
    print("gave up:", error.response.status_code, "| calls:", len(calls), "| slept:", sleep.delays)
```
```text
gave up: 404 | calls: 1 | slept: []
```

And when the failures do not stop, the helper gives up after `max_attempts` and raises the **last** error, so the caller (and the log) sees what actually went wrong:

```python
client, calls = scripted_client(503)                # 503 forever
sleep = FakeSleep()
try:
    call_with_retry(lambda: client.get("/v1/orders"), max_attempts=4, sleep=sleep, rand=lambda: 1.0)
except httpx.HTTPStatusError as error:
    print("gave up:", error.response.status_code, "| calls:", len(calls), "| slept:", sleep.delays)
```
```text
WARNING pipeline: attempt 1 got 503; retrying in 0.50s
WARNING pipeline: attempt 2 got 503; retrying in 1.00s
WARNING pipeline: attempt 3 got 503; retrying in 2.00s
gave up: 503 | calls: 4 | slept: [0.5, 1.0, 2.0]
```

Four attempts mean three waits: there is no point sleeping after the last attempt.

`call_with_retry` takes a function `send` (here a `lambda`) instead of a URL. That keeps it general: the same helper retries a GET with parameters, a GET of a next URL, or anything else that returns a response.

### 10.6 Retrying writes: idempotency keys

Everything above is about `GET`, which only reads. Retrying a **write** (a `POST` that creates a payment, say) is dangerous: if the first request succeeded but the response was lost on the way back, a retry creates a **second** payment. Many APIs solve this with an **idempotency key**: the client sends a unique value in a header (`Idempotency-Key: 3f2a...`), and the server remembers it; if the same key arrives again, the server returns the first result instead of acting twice. It is the same idea as the keyed upsert, applied by the server. If you ever write a pipeline that **sends** data to an API, look for this feature before you add retries.

### 10.7 Retry budgets and where to retry

A few more rules that keep retries from causing their own problems:

- **Retry at one level only.** If the HTTP helper retries 5 times, and the page loop retries each page 5 times, and the scheduler retries the job 5 times, one dead server causes 125 attempts per page. Retry requests in one place (the helper), and let the job fail cleanly if that is not enough.
- **Have a total budget**, not just a count: "give up if retries have taken more than 10 minutes in total". Exponential delays add up fast.
- **Log every retry** at `WARNING` with the attempt number and the reason, but not the request headers (they may contain tokens).
- **Make the whole run resumable** (section 11). Then "give up and fail" is cheap: the next run continues where this one stopped.

### 10.8 Try it: retries

**Try it 25.** With `base=0.5`, `max_delay=30`, `rand=lambda: 1.0` and `max_attempts=6`, what delays does `call_with_retry` sleep for a server that answers 502 five times and then 200? And with `rand=lambda: 0.0`?

<details><summary>Answer</summary>

Plain backoff for attempts 0 to 4 is `0.5 * 2**a`: 0.5, 1, 2, 4, 8. The sixth call succeeds, so there are five waits. With equal jitter, `rand` returning 1.0 gives the full backoff, and `rand` returning 0.0 leaves only the fixed half: 0.25, 0.5, 1, 2, 4.

```python
quiet = logging.getLogger("quiet")
quiet.disabled = True                       # only to keep this example's output short
for r in (1.0, 0.0):
    client, calls = scripted_client(502, 502, 502, 502, 502, 200)
    sleep = FakeSleep()
    response = call_with_retry(lambda: client.get("/"), max_attempts=6, sleep=sleep, rand=lambda: r,
                               logger=quiet)
    print(r, response.status_code, len(calls), sleep.delays)
```
```text
1.0 200 6 [0.5, 1.0, 2.0, 4.0, 8.0]
0.0 200 6 [0.25, 0.5, 1.0, 2.0, 4.0]
```

(The `logger` argument lets the caller choose where retry warnings go; here a disabled logger hides them, so only the results are printed.)

</details>

**Try it 26.** For each response, should a pipeline retry? (a) 401 after the API token expired; (b) 503 with `Retry-After: 20`; (c) `httpx.ConnectError`; (d) 400 with body `{"error": "per_page must be <= 100"}`; (e) 200 with an HTML body.

<details><summary>Answer</summary>

(a) **No**: a human (or a token-refresh step) must fix the credentials; repeating the same bad token can lock the account. (b) **Yes**, after 20 seconds. (c) **Yes**, with backoff: the network or server may be briefly down. (d) **No**: the request is wrong; fix `per_page` in the code or config. (e) **Maybe once or twice**: it is often a proxy or load balancer error page during a deploy; but if it continues, fail with a clear `BadResponse` message (section 2.5) rather than retrying for ever.

</details>

## 11. Checkpoints and resume

### 11.1 What a checkpoint is

A run that fetches 2,000 pages takes an hour. At page 1,400 the network drops for longer than the retries can cover, and the run fails. Without a checkpoint, the next run starts from page 1 and spends 40 minutes re-fetching what it already had. With a checkpoint, it starts from page 1,401.

A **checkpoint** is the smallest piece of state that lets a run continue from where it stopped. For an API extract that is usually:

- the **cursor** (or next page number, or next URL) for the next page to fetch;
- the **run id**, so you know the checkpoint belongs to this run and not an old one;
- for incremental loads, the **watermark** the run started from (`updated_since`), so the resumed run keeps asking the same question.

Do **not** put the data itself in the checkpoint. The checkpoint says "where am I"; the sink holds "what I have".

### 11.2 Atomic writes: temp file, then `os.replace`

A checkpoint file is tiny, so writing it seems trivial:

```python
path.write_text(json.dumps(state))
```

But `write_text` first **empties** the file and then writes the new content. If the program is killed between those two steps (power loss, the process is stopped, the disk fills), the file is left empty or half-written. On the next run, the checkpoint cannot be read, and you have lost exactly the information you needed to recover. Here is a simulated crash halfway through a write:

```python
import json
from pathlib import Path

path = Path("checkpoint.json")
path.write_text(json.dumps({"run_id": "run-007", "next_cursor": "eyJhZnRlciI6IDEwM30="}), encoding="utf-8")

def crashing_write(path, state):
    text = json.dumps(state)
    with path.open("w", encoding="utf-8") as f:       # "w" has already emptied the file here
        f.write(text[: len(text) // 2])               # half the data reaches the file...
        raise SystemExit("power cut (simulated)")     # ...then the process dies

try:
    crashing_write(path, {"run_id": "run-007", "next_cursor": "eyJhZnRlciI6IDEwNn0="})
except SystemExit as stop:
    print("crashed:", stop)
print("file now holds:", repr(path.read_text(encoding="utf-8")))
json.loads(path.read_text(encoding="utf-8"))
```
```text
crashed: power cut (simulated)
file now holds: '{"run_id": "run-007", "next_cu'
Traceback (most recent call last):
  ...
json.decoder.JSONDecodeError: Unterminated string starting at: line 1 column 23 (char 22)
```

The old checkpoint is gone and the new one is broken. The fix is an **atomic write**:

1. write the new content to a **temporary file in the same folder**;
2. flush it and ask the operating system to put it on disk (`os.fsync`);
3. **rename** the temporary file over the real one with `os.replace`.

Why step 2? Writing goes through two buffers. `f.write` puts the text in Python's buffer; `f.flush()` hands it to the operating system, which keeps it in memory (its **page cache**) and writes it to the disk "soon", when it suits it. `os.fsync(f.fileno())` waits until the data has really reached the disk. Without it, after a **power cut** the disk can contain the rename (the new name points at the temporary file) but not the data that was in it, so you get an empty or garbage checkpoint after all, the very thing the atomic write was meant to prevent. A plain crash of your program does not need `fsync` (the operating system still holds the data), but a crash of the whole machine does, and it costs only a few milliseconds per checkpoint.

`os.replace` is atomic: other programs (and the next run) see either the complete old file or the complete new file, never a mix. It works on Linux, macOS and Windows, and it overwrites an existing target (unlike `os.rename` on Windows, which refuses to). The temporary file must be in the **same folder**, because a rename is only atomic within one file system; moving across drives is a copy, which is not atomic.

```python
import json
import os
from pathlib import Path

def write_json_atomic(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

class CorruptCheckpoint(Exception):
    pass

def load_checkpoint(path):
    """Return the saved dict, or None if there is no checkpoint. Raise CorruptCheckpoint if unreadable."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise CorruptCheckpoint(f"{path} is not valid JSON ({error}); "
                                "inspect it, then delete it to start a fresh run") from None
    if not isinstance(data, dict):
        raise CorruptCheckpoint(f"{path} should hold a JSON object, found {type(data).__name__}")
    return data
```

Now the same crash, but in the middle of writing the **temporary** file:

```python
write_json_atomic(path, {"run_id": "run-007", "next_cursor": "eyJhZnRlciI6IDEwM30="})

def crashing_atomic_write(path, data):
    tmp = path.with_name(path.name + ".tmp")
    text = json.dumps(data)
    with tmp.open("w", encoding="utf-8") as f:
        f.write(text[: len(text) // 2])
        raise SystemExit("power cut (simulated)")
    os.replace(tmp, path)                          # never reached

try:
    crashing_atomic_write(path, {"run_id": "run-007", "next_cursor": "eyJhZnRlciI6IDEwNn0="})
except SystemExit:
    pass
print("checkpoint:", load_checkpoint(path))
print("leftover temp file:", repr(Path("checkpoint.json.tmp").read_text(encoding="utf-8")))
print("missing file:", load_checkpoint(Path("no-such-checkpoint.json")))
```
```text
checkpoint: {'next_cursor': 'eyJhZnRlciI6IDEwM30=', 'run_id': 'run-007'}
leftover temp file: '{"run_id": "run-007", "next_cu'
missing file: None
```

The real checkpoint still holds the last complete state. The half-written temporary file is garbage, but harmless: nothing reads it, and the next successful write replaces it. `load_checkpoint` returns `None` for a missing file, which means "no run in progress, start fresh".

What should happen when the checkpoint **is** corrupt (someone edited it by hand, or it was written by a buggy old version)? There are two defensible choices: raise a clear error so a human looks (shown above), or log a warning and start fresh. Starting fresh is only safe if the sink is idempotent, because a fresh start re-fetches everything already loaded. Since our sinks are idempotent, either works; raising is the more careful default, because a corrupt state file usually means something else is wrong too.

```python
Path("bad.json").write_text('{"run_id": "run-007", "next_cur', encoding="utf-8")
try:
    load_checkpoint(Path("bad.json"))
except CorruptCheckpoint as error:
    print(error)
```
```text
bad.json is not valid JSON (Unterminated string starting at: line 1 column 23 (char 22)); inspect it, then delete it to start a fresh run
```

Use the same temp-then-replace pattern for **every output file** a pipeline writes (CSV exports, Parquet files, reports), not only checkpoints. Then a reader never sees half a file.

### 11.3 Data first, checkpoint second

The order of the two writes in each step decides what a crash can do. There are only two possible orders:

**Order A (correct): save the page's data, then save the checkpoint.**

| Crash happens... | State after the crash | What the resumed run does | Result |
|---|---|---|---|
| before the data commit | data: up to page N-1; checkpoint: page N | fetches page N again | correct |
| after data, before checkpoint | data: up to page N; checkpoint: still page N | fetches page N **again**; upsert absorbs it | correct (one page fetched twice) |
| after the checkpoint | data: up to N; checkpoint: page N+1 | continues with N+1 | correct |

**Order B (wrong): save the checkpoint, then the data.**

| Crash happens... | State after the crash | What the resumed run does | Result |
|---|---|---|---|
| after checkpoint, before data | data: up to N-1; checkpoint: page N+1 | continues with N+1 | **page N is lost forever** |

Order A can only ever **repeat** work, which an idempotent sink makes harmless. Order B can **skip** work, which nothing downstream can detect. This is the same rule as for watermarks (section 8.5), and the same lesson as section 8.3: prefer the mistake that duplicates, and make duplicates harmless.

### 11.4 A resumable cursor fetch, with a crash injected

Here is a full resumable extract. It uses the cursor API from section 3.4, upserts each page into SQLite, and saves the next cursor atomically **after** each page commits. To test it, the mock server raises a `ConnectError` on a chosen call, standing in for a network failure that outlasts the retries.

```python
import base64

def encode_cursor(last_id):
    return base64.urlsafe_b64encode(json.dumps({"after": last_id}).encode()).decode()

def cursor_client(orders, requests, fail_on_call=None):
    def handler(request):
        requests.append(dict(request.url.params))
        if len(requests) == fail_on_call:
            raise httpx.ConnectError("network down (simulated)", request=request)
        params = request.url.params
        after = json.loads(base64.urlsafe_b64decode(params["cursor"]))["after"] if "cursor" in params else 0
        rows = [o for o in sorted(orders, key=lambda o: o["id"]) if o["id"] > after]
        limit = int(params.get("limit", "3"))
        chunk = rows[:limit]
        return httpx.Response(200, json={"items": chunk,
                                         "next_cursor": encode_cursor(chunk[-1]["id"]) if len(rows) > limit else None})
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.pagebound.test")

def resumable_fetch(con, client, checkpoint_path, run_id, limit=3):
    state = load_checkpoint(checkpoint_path)
    if state is not None and state.get("done"):
        state = None                                    # the last run finished; start a new one
    cursor = state["next_cursor"] if state else None
    pages = 0
    while True:
        params = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        body = client.get("/v1/orders", params=params).raise_for_status().json()
        with con:                                       # 1. data first
            upsert_orders(con, body["items"])
        pages += 1
        cursor = body["next_cursor"]
        write_json_atomic(checkpoint_path,              # 2. then the checkpoint
                          {"run_id": run_id, "next_cursor": cursor, "done": cursor is None})
        if cursor is None:
            return pages

con = sqlite3.connect(":memory:")
setup_db(con)
ckpt = Path("orders.checkpoint.json")
requests = []

try:
    resumable_fetch(con, cursor_client(ORDERS, requests, fail_on_call=3), ckpt, run_id="run-010")
except httpx.ConnectError as error:
    print("run 1 crashed:", error)
print("rows after crash:", con.execute("SELECT COUNT(*) FROM orders").fetchone()[0])
print("checkpoint:", load_checkpoint(ckpt))
```
```text
run 1 crashed: network down (simulated)
rows after crash: 6
checkpoint: {'done': False, 'next_cursor': 'eyJhZnRlciI6IDEwNn0=', 'run_id': 'run-010'}
```

The crash came on the third request. Pages 1 and 2 (six orders) were committed, and the checkpoint holds the cursor for page 3. Now the resumed run, against a healthy server:

```python
requests.clear()
pages = resumable_fetch(con, cursor_client(ORDERS, requests), ckpt, run_id="run-010")
print("resumed run made", len(requests), "request(s), fetched", pages, "page(s):", requests)
print("rows:", con.execute("SELECT COUNT(*), COUNT(DISTINCT id) FROM orders").fetchone())
print("checkpoint:", load_checkpoint(ckpt))
```
```text
resumed run made 1 request(s), fetched 1 page(s): [{'limit': '3', 'cursor': 'eyJhZnRlciI6IDEwNn0='}]
rows: (7, 7)
checkpoint: {'done': True, 'next_cursor': None, 'run_id': 'run-010'}
```

The resumed run made **one** request instead of three, all seven orders are present exactly once, and the checkpoint is marked `done`. Starting from scratch would also have given seven rows (the upsert makes it safe), just with more requests; the checkpoint saves time, and the idempotent sink guarantees correctness. You want both.

Now the same crash with the **wrong order** (checkpoint first, then data). To show it, the crash is injected in the load step, between the two writes:

```python
def wrong_order_fetch(con, client, checkpoint_path, crash_on_page=None):
    state = load_checkpoint(checkpoint_path)
    cursor = state["next_cursor"] if state and not state.get("done") else None
    page = 0
    while True:
        params = {"limit": 3, **({"cursor": cursor} if cursor else {})}
        body = client.get("/v1/orders", params=params).raise_for_status().json()
        page += 1
        cursor = body["next_cursor"]
        write_json_atomic(checkpoint_path, {"next_cursor": cursor, "done": cursor is None})   # checkpoint FIRST
        if page == crash_on_page:
            raise SystemExit("crashed before the data was written (simulated)")
        with con:
            upsert_orders(con, body["items"])
        if cursor is None:
            return

con2 = sqlite3.connect(":memory:")
setup_db(con2)
bad_ckpt = Path("wrong.checkpoint.json")
try:
    wrong_order_fetch(con2, cursor_client(ORDERS, []), bad_ckpt, crash_on_page=2)
except SystemExit as stop:
    print(stop)
wrong_order_fetch(con2, cursor_client(ORDERS, []), bad_ckpt)
print("ids loaded:", [r[0] for r in con2.execute("SELECT id FROM orders ORDER BY id")])
```
```text
crashed before the data was written (simulated)
ids loaded: [101, 102, 103, 107]
```

Orders 104, 105 and 106 are missing, the run "finished successfully", and nothing anywhere records the loss. That is why the order of two lines matters so much.

### 11.5 Checkpoint in the database: one transaction for both

When the sink is a database, there is an even stronger option: store the checkpoint **in the same database** and update it **in the same transaction** as the page's data. Then there is no "between" at all: either the page and its checkpoint are both saved, or neither is.

```python
def fetch_page_and_checkpoint(con, body, run_id):
    with con:                                            # ONE transaction
        upsert_orders(con, body["items"])
        set_state(con, "cursor_run", run_id)
        set_state(con, "next_cursor", body["next_cursor"])

con = sqlite3.connect(":memory:")
setup_db(con)
fetch_page_and_checkpoint(con, {"items": ORDERS[:3], "next_cursor": "eyJhZnRlciI6IDEwM30="}, "run-011")
print(con.execute("SELECT * FROM pipeline_state ORDER BY name").fetchall())
print(con.execute("SELECT COUNT(*) FROM orders").fetchone())
```
```text
[('cursor_run', 'run-011'), ('next_cursor', 'eyJhZnRlciI6IDEwM30=')]
(3,)
```

This is the best design when the data and the state live in one database. When they cannot (data goes to Parquet files, state in a JSON file), use the order "data first, checkpoint second" with atomic file writes, and make the data writes idempotent.

### 11.6 Finishing a run

When a run completes, the checkpoint must stop saying "continue from here", or the next run will think it is resuming. Either delete the checkpoint file, or keep it with `"done": true` (as above) so the next run knows to start fresh. Keeping it has a benefit: you can see when the last run finished and how far it got.

For incremental pipelines, finishing a run is also the moment to move the **watermark** (section 8.5): the run started with `updated_since = W`, saved that `W` in the checkpoint so a resume asks the same question, and only when every page is loaded does the watermark move to the newest `updated_at` seen.

### 11.7 Try it: checkpoints

**Try it 27.** A pipeline saves data first and the checkpoint second, with an idempotent upsert. The program is killed at each of these moments. For each, how many times is page 5 fetched in total (across the crashed run and the resumed one), and is any data lost? (a) while page 5's request is in flight; (b) after page 5's data commits, before its checkpoint is written; (c) after page 5's checkpoint is written.

<details><summary>Answer</summary>

(a) Page 5 was never received; the checkpoint still points to page 5; the resume fetches it: **once** successfully (the in-flight request does not count as a fetch that delivered data). (b) Page 5's data is in the sink, but the checkpoint still points to page 5, so the resume fetches it **again**: twice in total. The upsert writes nothing new. No loss. (c) The checkpoint points to page 6; page 5 is fetched **once**. No data is lost in any case; the worst case is one repeated page.

</details>

**Try it 28.** Why must the temporary file for an atomic write be in the same folder as the target, rather than in the system's temp folder (such as `/tmp` or `C:\Users\you\AppData\Local\Temp`)?

<details><summary>Answer</summary>

A rename is atomic only when source and target are on the same file system (the same drive or partition). The system temp folder is often on a different one. Then `os.replace` either fails (on Linux, with `OSError: Invalid cross-device link`) or the operation becomes a copy followed by a delete, which can be interrupted halfway, defeating the purpose. A temp file next to the target (`checkpoint.json.tmp`) is always on the same file system.

</details>

## 12. Logging and run summaries

### 12.1 Why a pipeline needs logs

A pipeline runs at three in the morning with nobody watching. When finance says "yesterday's numbers look low", the log is the only witness. A useful log answers:

- **Which run** is this? (a run id, the start time, the configuration)
- **What did it do?** (pages fetched, records received, written, skipped, quarantined)
- **How long did it take?** (overall and per step, so you notice when it slows down)
- **What went wrong?** (retries with reasons, quarantined records by id, the error that stopped it)

`print` is not enough. You met the `logging` module earlier in the course; pipelines rely on its features: **levels** (DEBUG, INFO, WARNING, ERROR) to control how much detail appears, a **format** with time and source, and **handlers** to send output to a file or the console without changing the code that logs.

### 12.2 A basic setup

Configure logging **once**, at the program's entry point, not inside library functions. Every module gets its own logger by name; here everything uses `"pipeline"`.

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)-7s %(name)s: %(message)s",      # real pipelines add %(asctime)s at the front
)
log = logging.getLogger("pipeline")

log.debug("not shown: the level is INFO")
log.info("starting run %s", "run-012")
log.warning("page %d: %d record(s) quarantined", 2, 1)
```
```text
INFO    pipeline: starting run run-012
WARNING pipeline: page 2: 1 record(s) quarantined
```

The format here leaves out the time so that the example output is the same every time you run it. In real use, put `%(asctime)s` first: `"%(asctime)s %(levelname)-7s %(name)s: %(message)s"`, which prints something like `2024-06-05 03:00:01,234 INFO    pipeline: starting run run-012` (the time is from your clock).

Note the style `log.info("starting run %s", run_id)`, with the values passed separately, not `log.info(f"starting run {run_id}")`. With the `%s` style, the message is only built if it will actually be shown, which matters for DEBUG lines inside loops; and log tools can group messages by their template.

### 12.3 Run ids

Every run should have an id that appears on every log line and in every table row it writes (`run_id` in the raw layer, the quarantine file, the runs table). Then "which run wrote this bad row?" is one query or one `grep`.

```python
import uuid
from datetime import datetime, timezone

def new_run_id(now):
    return now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]

u = uuid.uuid4()                      # a random 128-bit id; different on every call
print(u)
print(u.hex, "->", u.hex[:8])
print(new_run_id(datetime(2024, 6, 5, 3, 0, tzinfo=timezone.utc)))   # the last 8 characters are random
```
```text
bb9d8d03-6c0b-4334-94a6-d56b6a3f5c91
bb9d8d036c0b433494a6d56b6a3f5c91 -> bb9d8d03
20240605T030000Z-5c401df9
```

`uuid.uuid4()` makes a random **UUID** (universally unique identifier); `.hex` is the same value as 32 hexadecimal characters without dashes. Eight of those characters (32 random bits, about four billion possibilities) are plenty to tell runs apart, and short enough to read in a log line. A time prefix makes ids sort in run order and tells you at a glance when the run happened; the random suffix keeps two runs started in the same second apart. (All three printed values are random: your output will differ.)

### 12.4 Counts, durations, and one summary line

The most useful single line in a pipeline log is the **summary** at the end. It should be one line, with fixed `key=value` pairs, so both people and scripts can read it:

```text
run=20240605T030000Z-a1b2c3 status=ok pages=3 fetched=7 written=5 unchanged=2 quarantined=0 seconds=1.42
```

Counting is easy if you keep the numbers in one place as the run goes. A small dataclass works well:

```python
import logging
import sys
import time
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("pipeline")

@dataclass
class RunStats:
    run_id: str
    pages: int = 0
    fetched: int = 0
    written: int = 0
    quarantined: int = 0
    retries: int = 0
    started: float = field(default_factory=time.perf_counter, repr=False)

    def summary(self, status):
        seconds = time.perf_counter() - self.started
        counts = {k: v for k, v in asdict(self).items() if k not in ("run_id", "started")}
        pairs = " ".join(f"{k}={v}" for k, v in counts.items())
        return f"run={self.run_id} status={status} {pairs} seconds={seconds:.2f}"

con = sqlite3.connect(":memory:")
setup_db(con)
stats = RunStats(run_id="run-013")
for page, data in [(1, ORDERS[:3]), (2, ORDERS[3:6]), (3, ORDERS[6:])]:
    with con:
        written = upsert_orders(con, data)
    stats.pages += 1
    stats.fetched += len(data)
    stats.written += written
    log.debug("page %d: fetched=%d written=%d", page, len(data), written)
log.info(stats.summary("ok"))
```
```text
INFO    pipeline: run=run-013 status=ok pages=3 fetched=7 written=7 quarantined=0 retries=0 seconds=0.00
```

(The `seconds` value is a timing from this machine; yours will differ.)

Durations use `time.perf_counter()`, a clock meant for measuring intervals: it never jumps when the system clock is adjusted, unlike `time.time()`. Use `datetime.now(timezone.utc)` for **when** something happened, and `perf_counter` for **how long** it took.

### 12.5 Levels: what goes where

| Level | Use it for | Example |
|---|---|---|
| DEBUG | detail you need only when hunting a bug | each page's params and counts |
| INFO | the normal story of a run | run started (with config), run summary |
| WARNING | something odd that did not stop the run | a retry, a quarantined record, a null rate above normal |
| ERROR | the run (or a step) failed | "aborting: 80 of 1000 records failed" |

In production you run at INFO, so a normal run logs a handful of lines; when something is wrong you re-run at DEBUG. A log that prints a line per record at INFO is a log nobody reads.

When the run fails, log the exception **with its traceback** using `log.exception(...)` inside the `except` block (it logs at ERROR and adds the traceback), then re-raise so the scheduler sees the failure:

```python
def run(stats):
    try:
        raise httpx.ConnectError("network down (simulated)")
    except Exception:
        log.exception("run %s failed after %d pages", stats.run_id, stats.pages)
        log.error(stats.summary("failed"))
        raise

try:
    run(RunStats(run_id="run-014"))
except httpx.ConnectError:
    pass
```
```text
ERROR   pipeline: run run-014 failed after 0 pages
Traceback (most recent call last):
  File "<example>", line 3, in run
httpx.ConnectError: network down (simulated)
ERROR   pipeline: run=run-014 status=failed pages=0 fetched=0 written=0 quarantined=0 retries=0 seconds=0.00
```

The traceback here is short because the example is tiny (and `<example>` stands for this chapter's code block); in a real log it lists every file, line number and source line on the way to the error, which is exactly what you need to debug a 3 a.m. failure. Note that the failed run still logs a summary with `status=failed`, so a dashboard that reads summary lines sees every run, good or bad.

Catching `Exception` here is right, unlike in the per-record handler of section 7.3: at the top level of a run you want to log **any** failure, including bugs, and then you **re-raise** it, so nothing is hidden.

### 12.6 What never to log

Logs are copied to many places (log files, monitoring tools, chat alerts, bug reports) and read by many people. They are usually protected less carefully than the database. So some things must **never** appear in a log:

- **Secrets**: API tokens, passwords, keys, the `Authorization` header, connection strings with passwords in them.
- **Personal data**: emails, names, phone numbers, addresses, the full record. Log the **id** of a bad record (`order 104 quarantined: amount not a number`), not the record.
- **Anything you would not want in a screenshot** in a public bug report.

Two common leaks to watch for:

1. **Logging a whole record or a whole response** "for debugging" (`log.warning("bad record: %s", record)`). That writes the customer's email into the log.
2. **Tokens in URLs.** If an API takes the token as a query parameter (`?api_key=...`), every log line that prints a URL leaks it. httpx itself logs every request's full URL, query string included, at INFO level through a logger named `"httpx"` (you will see those lines in section 17.3). Send tokens in a header instead, never log headers, and turn the `httpx` logger down to WARNING in production with `logging.getLogger("httpx").setLevel(logging.WARNING)` if you do not need a line per request.

As a safety net (not a replacement for care), a logging **filter** can mask anything that looks like an email before the line is written:

```python
import logging
import re
import sys

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

class RedactEmails(logging.Filter):
    def filter(self, record):
        record.msg = EMAIL.sub("<email>", record.getMessage())
        record.args = ()
        return True                                   # keep the record, just cleaned

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
handler.addFilter(RedactEmails())
log = logging.getLogger("pipeline.safe")
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False

log.warning("order %d quarantined; customer %s", 104, "dia@example.com")
log.info("no personal data here: %d records", 7)
```
```text
WARNING pipeline.safe: order 104 quarantined; customer <email>
INFO pipeline.safe: no personal data here: 7 records
```

The filter works on the final message (`record.getMessage()` fills in the `%` arguments first), replaces anything shaped like an email, and then clears `args` so the formatter does not try to fill them in again.

### 12.7 A runs table

Logs are text; questions like "how many records did each run write last week?" are easier with a table. Many pipelines record each run in the database:

```python
con = sqlite3.connect(":memory:")
con.execute("""CREATE TABLE runs (
    run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
    status TEXT NOT NULL, fetched INTEGER, written INTEGER, quarantined INTEGER, error TEXT)""")

def start_run(con, run_id, started_at):
    with con:
        con.execute("INSERT INTO runs (run_id, started_at, status) VALUES (?, ?, 'running')", (run_id, started_at))

def finish_run(con, run_id, finished_at, status, fetched, written, quarantined, error=None):
    with con:
        con.execute("""UPDATE runs SET finished_at = ?, status = ?, fetched = ?, written = ?,
                       quarantined = ?, error = ? WHERE run_id = ?""",
                    (finished_at, status, fetched, written, quarantined, error, run_id))

start_run(con, "run-015", "2024-06-05T03:00:00Z")
finish_run(con, "run-015", "2024-06-05T03:00:42Z", "ok", 7, 7, 0)
start_run(con, "run-016", "2024-06-05T04:00:00Z")
finish_run(con, "run-016", "2024-06-05T04:03:10Z", "failed", 300, 300, 0, "ConnectError: network down")
start_run(con, "run-017", "2024-06-05T05:00:00Z")        # still running, or died without finishing
for row in con.execute("SELECT run_id, status, fetched, written, error FROM runs ORDER BY started_at"):
    print(row)
```
```text
('run-015', 'ok', 7, 7, None)
('run-016', 'failed', 300, 300, 'ConnectError: network down')
('run-017', 'running', None, None, None)
```

A run whose status stays `running` long after it should have finished is a run that died without even logging its failure (the machine was switched off, the process was killed). A runs table makes those visible: `SELECT * FROM runs WHERE status = 'running' AND started_at < ?`.

### 12.8 Try it: logging

**Try it 29.** Find three problems in this logging code:

```python
log.info(f"Fetched page {page} from {client.base_url} with headers {client.headers}")
for record in bad_records:
    log.info("Bad record: %s", record)
```

<details><summary>Answer</summary>

1. **The headers are logged**, and they contain the `Authorization` token. Anyone who can read the log can now call the API as the pipeline.
2. **Whole records are logged**, which writes customers' emails (personal data) into the log. Log the id and the reason instead.
3. **The levels are wrong**: a line per page at INFO is noisy (that is DEBUG), and a bad record is a WARNING, not INFO. A smaller fourth point: the first line uses an f-string, so the message is built even when it would not be shown; use `log.debug("fetched page %d", page)`.

</details>

**Try it 30.** Your run summary says `fetched=1000 written=0 quarantined=0`. The run "succeeded". Is something wrong? What would you check?

<details><summary>Answer</summary>

Maybe, maybe not. `written=0` with `fetched=1000` means every record was either unchanged or older than what is stored. That is **normal** if the run re-fetched an overlap window or re-ran after a crash. It is **suspicious** if it happens on a run that should have seen new data (a normal hourly run). Check: did the watermark move? What is the newest `updated_at` in the fetched data compared with the table's newest? Is the source frozen (freshness check, section 6.3)? Did someone point the pipeline at a test API that returns the same data? This is why the summary should include enough counts (fetched, written, unchanged) to tell these cases apart.

</details>

## 13. Files: CSV vs Parquet

### 13.1 Why files at all

The SQLite database serves finance. Analysts want something else: files they can copy, open in many tools (a notebook, a spreadsheet, a data warehouse, a dashboard tool) and read in bulk, months at a time, without querying a live database. Two formats dominate:

- **CSV** (comma-separated values): plain text, one line per row, values separated by commas. Every tool on Earth reads it.
- **Parquet**: a binary, **columnar**, typed, compressed format, designed for analysis. Most data tools read it, and it is the default file format of modern data lakes.

### 13.2 What CSV forgets

CSV is text, and only text. It has no types, no schema, and no standard way to say "null". Write the flattened orders to CSV and read them back, and see what comes back:

```python
import csv
from pathlib import Path

rows = [flatten_order(o) for o in ORDERS[:2]]
path = Path("orders.csv")
with path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print(path.read_text(encoding="utf-8"))
with path.open(encoding="utf-8", newline="") as f:
    back = list(csv.DictReader(f))
for key in ["id", "customer_city", "amount", "created_at", "qty_total"]:
    print(f"{key:14} wrote {rows[1][key]!r:45} read {back[1][key]!r}")
```
```text
id,customer_email,customer_city,status,amount,currency,created_at,updated_at,order_date,item_lines,qty_total
101,asha@example.com,Pune,shipped,19.99,INR,2024-06-01 10:00:00+00:00,2024-06-01 12:00:00+00:00,2024-06-01,1,2
102,ben@example.com,,pending,5.50,INR,2024-06-01 11:30:00+00:00,2024-06-01 12:30:00+00:00,2024-06-01,1,1

id             wrote 102                                           read '102'
customer_city  wrote None                                          read ''
amount         wrote Decimal('5.50')                               read '5.50'
created_at     wrote datetime.datetime(2024, 6, 1, 11, 30, tzinfo=datetime.timezone.utc) read '2024-06-01 11:30:00+00:00'
qty_total      wrote 1                                             read '1'
```

Every value came back as a string. The integer `102` is now `'102'`; the `Decimal` is `'5.50'`; the aware datetime is a string in a format CSV did not choose (it is just `str(datetime)`); and `None` came back as `''`, so you cannot tell "no city" from "a city with an empty name". The reader must know, from somewhere outside the file, that `id` is an integer, `amount` is money with two decimals, `created_at` is UTC, and empty means null. That "somewhere" is usually a document that is out of date.

Other CSV problems you will meet:

- **Quoting**: a value containing a comma, a quote or a newline must be quoted (`"Salt, and Stars"`). The `csv` module does this right; hand-written `",".join(...)` does not.
- **Encoding**: open with `encoding="utf-8"`. Excel on Windows may expect `utf-8-sig` (UTF-8 with a marker at the start) to show non-English text correctly.
- **`newline=""`**: always pass it when opening a CSV file with the `csv` module, or on Windows you get blank lines between rows.
- **Leading zeros and big numbers**: a spreadsheet opening `"007"` shows `7`, and a 16-digit id becomes `1.23457E+15`.

CSV is still the right choice for small exports that a person will open in a spreadsheet, for sending data to systems that only accept CSV, and for tiny test fixtures. For storing data that programs will read, use something typed.

### 13.3 What Parquet is

A Parquet file stores a table **by column**, not by row. Picture the same three orders stored both ways:

```text
row-oriented (CSV):          column-oriented (Parquet):
101,Pune,shipped,19.99       id:     101, 102, 103
102,,pending,5.50            city:   Pune, null, Delhi
103,Delhi,shipped,42.00      status: shipped, pending, shipped
                             amount: 19.99, 5.50, 42.00
```

Storing by column has three big benefits for analysis:

1. **Read only the columns you need.** "Total amount per day" needs two columns out of twenty; a Parquet reader skips the other eighteen entirely. A CSV reader must read every byte of every row.
2. **Compression works much better.** A column holds values of one type that are often similar (`shipped, shipped, pending, shipped`), and similar values compress very well. Parquet compresses each column (with Snappy by default in pyarrow; Zstandard and others are options) and uses tricks such as **dictionary encoding** (store `shipped` once and refer to it by a small number).
3. **The schema is stored in the file.** Column names, types (int64, decimal, timestamp with time zone, string), and which columns may be null are part of the file. A reader gets real types back without any outside document.

Inside, a Parquet file is split into **row groups** (blocks of rows, typically tens of thousands to millions), and each row group stores each column separately, with statistics such as the minimum and maximum value. A reader asking for `amount > 1000` can skip a whole row group whose maximum amount is 500 without reading it.

The costs: Parquet is binary (you cannot open it in a text editor), and it is made for writing a file **once** and reading it many times. You cannot append a row or change one value in place; you write a new file. That fits pipelines perfectly: they write a batch, then many people read it.

### 13.4 pyarrow basics: tables and schemas

`pyarrow` is the Python library for Apache Arrow, an in-memory columnar format, and it reads and writes Parquet. The central object is the **`pa.Table`**: a set of named, typed columns of equal length.

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.table({
    "id": [101, 102, 103],
    "city": ["Pune", None, "Delhi"],
    "amount": [19.99, 5.5, 42.0],
})
print(table.schema)
print(table.num_rows, table.column_names)
print(table.column("city"))
print(table.to_pylist()[1])
```
```text
id: int64
city: string
amount: double
3 ['id', 'city', 'amount']
[
  [
    "Pune",
    null,
    "Delhi"
  ]
]
{'id': 102, 'city': None, 'amount': 5.5}
```

`pa.table` **inferred** the types: Python ints became `int64`, strings became `string` (with `None` as null), and floats became `double` (a 64-bit float). Inference is convenient, but it guesses from the data you happen to have: a column that is all `None` in today's batch is inferred as type `null`, and tomorrow's file, with real values, has a different schema. For a pipeline, **declare the schema explicitly**:

```python
import pyarrow as pa
import pyarrow.parquet as pq

ORDER_ARROW_SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("customer_email", pa.string()),
    pa.field("customer_city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(12, 2), nullable=False),
    pa.field("currency", pa.string(), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("updated_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("order_date", pa.string(), nullable=False),
    pa.field("item_lines", pa.int32(), nullable=False),
    pa.field("qty_total", pa.int32(), nullable=False),
])
```

The types to know:

| pyarrow type | Holds | Python value |
|---|---|---|
| `pa.int64()`, `pa.int32()` | whole numbers (64 or 32 bit) | `int` |
| `pa.float64()` | floating point ("double") | `float` |
| `pa.decimal128(p, s)` | exact decimals: `p` digits in total, `s` after the point | `decimal.Decimal` |
| `pa.string()` | text | `str` |
| `pa.bool_()` | true/false | `bool` |
| `pa.timestamp("us", tz="UTC")` | an instant, in microseconds, with a time zone | aware `datetime` |
| `pa.date32()` | a calendar date | `datetime.date` |

`pa.decimal128(12, 2)` means up to 12 digits, 2 of them after the point: values up to 9,999,999,999.99, exactly. `nullable=False` is a promise that the column has no nulls. Be careful about **when** it is checked: building a table from Python values does not check it, but `pq.write_table` does, and refuses to write the file (Try it 32 shows both).

`pa.Table.from_pylist(rows, schema=...)` builds a table from a list of dicts, converting each value to the declared type:

```python
rows = [flatten_order(o) for o in ORDERS]
table = pa.Table.from_pylist(rows, schema=ORDER_ARROW_SCHEMA)
print(table.num_rows, "rows")
print(table.schema.field("amount"), "|", table.schema.field("created_at"))
print(table.column("amount").to_pylist()[:3])
```
```text
7 rows
pyarrow.Field<amount: decimal128(12, 2) not null> | pyarrow.Field<created_at: timestamp[us, tz=UTC] not null>
[Decimal('19.99'), Decimal('5.50'), Decimal('42.00')]
```

### 13.5 Writing and reading Parquet

`pq.write_table(table, path)` writes one file; `pq.read_table(path)` reads it back.

```python
from pathlib import Path
import datetime
import decimal

pq.write_table(table, "orders.parquet")
back = pq.read_table("orders.parquet")
print(back.schema == table.schema, back.equals(table))
row = back.to_pylist()[1]
for key in ["id", "customer_city", "amount", "created_at", "qty_total"]:
    print(f"{key:14} {row[key]!r:70} {type(row[key]).__name__}")
```
```text
True True
id             102                                                                    int
customer_city  None                                                                   NoneType
amount         Decimal('5.50')                                                        Decimal
created_at     datetime.datetime(2024, 6, 1, 11, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC')) datetime
qty_total      1                                                                      int
```

Everything came back exactly as it went in: an `int`, a real `None`, a `Decimal('5.50')`, an aware UTC `datetime`. (pyarrow attaches the time zone as `zoneinfo.ZoneInfo('UTC')` rather than `datetime.timezone.utc`; both mean UTC, and the two datetimes compare equal.) Compare that with the CSV round trip in section 13.2. No outside document is needed, because the schema travelled inside the file.

Reading only some columns is one argument:

```python
slim = pq.read_table("orders.parquet", columns=["order_date", "amount"])
print(slim.schema)
print(slim.slice(0, 2).to_pylist())
meta = pq.ParquetFile("orders.parquet").metadata
print("rows:", meta.num_rows, "| row groups:", meta.num_row_groups, "| columns:", meta.num_columns)
```
```text
order_date: string not null
amount: decimal128(12, 2) not null
[{'order_date': '2024-06-01', 'amount': Decimal('19.99')}, {'order_date': '2024-06-01', 'amount': Decimal('5.50')}]
rows: 7 | row groups: 1 | columns: 11
```

### 13.6 The schema protects you

An explicit schema is also a **check**: values that do not fit are rejected when the table is built, so bad data never reaches a file.

```python
import decimal
bad = flatten_order(ORDERS[0])
bad["amount"] = "19.99"                       # a str, where a Decimal is expected
try:
    pa.Table.from_pylist([bad], schema=ORDER_ARROW_SCHEMA)
except (pa.ArrowInvalid, pa.ArrowTypeError) as error:
    print(type(error).__name__, ":", error)

too_precise = flatten_order(ORDERS[0])
too_precise["amount"] = decimal.Decimal("19.999")
try:
    pa.Table.from_pylist([too_precise], schema=ORDER_ARROW_SCHEMA)
except (pa.ArrowInvalid, pa.ArrowTypeError) as error:
    print(type(error).__name__, ":", error)
```
```text
ArrowTypeError : int or Decimal object expected, got str
ArrowInvalid : Rescaling Decimal value would cause data loss
```

pyarrow refused a string in a decimal column, and refused to silently round `19.999` to two places. Both errors are what you want: loud, at write time, naming the problem. (`pa.ArrowInvalid` and `pa.ArrowTypeError` are the two exception classes you will see most; catching both is a good habit.)

### 13.7 Size and speed

Columnar storage and compression make Parquet much smaller than CSV for typical data. Here is a quick comparison on 100,000 rows that look like orders (repetitive, as real data is: few statuses, few cities, increasing ids):

```python
import csv
import os
import pyarrow as pa
import pyarrow.parquet as pq

n = 100_000
cities = ["Pune", "Delhi", "Mumbai", "Chennai", None]
statuses = ["shipped", "shipped", "shipped", "pending", "cancelled"]
data = {
    "id": list(range(1, n + 1)),
    "city": [cities[i % 5] for i in range(n)],
    "status": [statuses[(i * 7) % 5] for i in range(n)],
    "amount_cents": [500 + (i * 37) % 5000 for i in range(n)],
}
table = pa.table(data)
pq.write_table(table, "big.parquet")
with open("big.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(data.keys())
    writer.writerows(zip(*data.values()))

csv_size, pq_size = os.path.getsize("big.csv"), os.path.getsize("big.parquet")
print(f"CSV:     {csv_size:>9,} bytes")
print(f"Parquet: {pq_size:>9,} bytes   (about {csv_size / pq_size:.1f}x smaller)")

row_group = pq.ParquetFile("big.parquet").metadata.row_group(0)
for i in range(row_group.num_columns):
    column = row_group.column(i)
    print(f"   {column.path_in_schema:13} {column.total_compressed_size:>8,} bytes compressed")
```
```text
CSV:     2,558,924 bytes
Parquet:   748,897 bytes   (about 3.4x smaller)
   id             603,354 bytes compressed
   city             2,014 bytes compressed
   status           1,666 bytes compressed
   amount_cents   140,878 bytes compressed
```

(The byte counts are from this machine and this pyarrow version; with other versions or settings they may differ a little.) The whole file is a few times smaller, but the per-column numbers tell the real story. `status` and `city`, with only a handful of distinct values, shrink to almost nothing thanks to dictionary encoding. `id` (100,000 different numbers) and `amount_cents` (thousands of different values) are where the bytes go, because unique values cannot be compressed away. Real tables usually have many low-variety columns (statuses, cities, currencies, flags, dates), so Parquet files are commonly 3 to 10 times smaller than the same CSV. And a reader who needs only `status` reads a few kilobytes instead of the whole file.

### 13.8 Write output files atomically

A Parquet file written halfway is unreadable (the schema and the index are at the **end** of the file). So the rule from section 11.2 applies: write to a temporary name in the same folder, then `os.replace` it into place.

```python
def write_parquet_atomic(table, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    pq.write_table(table, tmp)
    os.replace(tmp, path)
```

Readers who open `orders.parquet` at any moment see either yesterday's complete file or today's complete file.

### 13.9 Try it: CSV and Parquet

**Try it 31.** Predict the output: the values and their Python types after each round trip.

```python
from decimal import Decimal
row = {"id": 7, "amount": Decimal("3.10"), "city": None, "ok": True}
# (a) csv.DictWriter then csv.DictReader;  (b) pa.Table.from_pylist with an inferred schema, write_table, read_table
```

<details><summary>Answer</summary>

```python
import csv
import io
from decimal import Decimal

row = {"id": 7, "amount": Decimal("3.10"), "city": None, "ok": True}

buffer = io.StringIO()
writer = csv.DictWriter(buffer, fieldnames=list(row))
writer.writeheader()
writer.writerow(row)
buffer.seek(0)
csv_back = next(csv.DictReader(buffer))
print("CSV:    ", {k: (v, type(v).__name__) for k, v in csv_back.items()})

pq.write_table(pa.Table.from_pylist([row]), "row.parquet")
pq_back = pq.read_table("row.parquet")
print("schema: ", pq_back.schema.types)
print("Parquet:", {k: (v, type(v).__name__) for k, v in pq_back.to_pylist()[0].items()})
```
```text
CSV:     {'id': ('7', 'str'), 'amount': ('3.10', 'str'), 'city': ('', 'str'), 'ok': ('True', 'str')}
schema:  [DataType(int64), Decimal128Type(decimal128(3, 2)), DataType(null), DataType(bool)]
Parquet: {'id': (7, 'int'), 'amount': (Decimal('3.10'), 'Decimal'), 'city': (None, 'NoneType'), 'ok': (True, 'bool')}
```

CSV turns everything into strings, including `True` into `'True'` and `None` into `''`. Parquet keeps the types; even the inferred schema made `Decimal("3.10")` a `decimal128(3, 2)` column, so it comes back as a `Decimal`. The `city` column is all null, so its type is inferred as `null`, which shows why you declare schemas: a file with real cities would have type `string`, and the two files would not match.

</details>

**Try it 32.** Using `ORDER_ARROW_SCHEMA`, what happens if a row's `qty_total` is `3.0` (a float)? If it is `3.5`? If `customer_city` is missing from the dict entirely? And if `status` (declared `nullable=False`) is missing?

<details><summary>Answer</summary>

```python
r1 = flatten_order(ORDERS[0]); r1["qty_total"] = 3.0
r2 = flatten_order(ORDERS[0]); r2["qty_total"] = 3.5
r3 = flatten_order(ORDERS[0]); del r3["customer_city"]
for label, r in [("qty 3.0", r1), ("qty 3.5", r2), ("missing city", r3)]:
    try:
        t = pa.Table.from_pylist([r], schema=ORDER_ARROW_SCHEMA)
        print(label, "-> ok:", t.column("qty_total").to_pylist(), t.column("customer_city").to_pylist())
    except (pa.ArrowInvalid, pa.ArrowTypeError) as error:
        print(label, "->", type(error).__name__, error)

r4 = flatten_order(ORDERS[0]); del r4["status"]               # status is declared nullable=False
t = pa.Table.from_pylist([r4], schema=ORDER_ARROW_SCHEMA)
print("missing status -> table built, status =", t.column("status").to_pylist())
try:
    pq.write_table(t, "no-status.parquet")
except pa.ArrowInvalid as error:
    print("write_table ->", error)
```
```text
qty 3.0 -> ok: [3] ['Pune']
qty 3.5 -> ok: [3] ['Pune']
missing city -> ok: [2] [None]
missing status -> table built, status = [None]
write_table -> Column 'status' is declared non-nullable but contains nulls
```

Every one of them builds a table without complaint, and two are traps. `3.0` becomes the integer 3, which is harmless. But `3.5` **also** becomes 3: pyarrow silently truncated the fraction when converting a Python float into an `int32` column. A missing key is quietly treated as **null**: fine for the nullable `customer_city`, but for `status`, declared `nullable=False`, the table is built with a null in it anyway, and only `pq.write_table` finally refuses. So the Arrow schema is a useful last line of defence (it did reject a string in a decimal column and a decimal with too many places, in section 13.6), but it is not a contract check: it does not notice a missing key, and it can change a value without telling you. Validate records before this point (section 6), where you can quarantine them with a readable reason.

</details>

## 14. Partitioning

### 14.1 Why split the data into folders

A year of orders in one Parquet file is a problem twice over. To read one day, a reader must open the whole file (statistics help, but not completely). And to **replace** one day (because orders for that day changed) the pipeline must rewrite the whole year.

**Partitioning** splits a dataset into folders by the value of a column, usually a date. Each folder holds only the rows for its value:

```text
orders/
├── order_date=2024-06-01/
│   └── part-0.parquet
├── order_date=2024-06-02/
│   └── part-0.parquet
└── order_date=2024-06-03/
    └── part-0.parquet
```

This layout, with `column=value` folder names, is called **Hive-style** partitioning (after the Apache Hive project that made it popular). Almost every data tool understands it. The benefits follow directly:

- **Partition pruning**: a reader asking for `order_date = '2024-06-02'` opens only that folder.
- **Partition replacement**: the pipeline can rewrite one day's folder without touching any other day. This is section 9.6's "delete and insert per partition", for files.
- **Retention**: deleting data older than a year is deleting folders.

The partition column's value lives in the **folder name**, not inside the files. Readers add it back as a column when they read the dataset.

### 14.2 Writing a partitioned dataset

`pq.write_to_dataset(table, root, partition_cols=[...])` writes one folder per distinct value:

```python
from pathlib import Path
import pyarrow.dataset as ds

def tree(root):
    for path in sorted(Path(root).rglob("*.parquet")):
        print("   ", path.relative_to(root).as_posix())

table = pa.Table.from_pylist([flatten_order(o) for o in ORDERS], schema=ORDER_ARROW_SCHEMA)
pq.write_to_dataset(table, "lake/orders", partition_cols=["order_date"])
tree("lake/orders")
```
```text
    order_date=2024-06-01/34bbc317b682422b9ba92ad0575c0fb4-0.parquet
    order_date=2024-06-02/34bbc317b682422b9ba92ad0575c0fb4-0.parquet
    order_date=2024-06-03/34bbc317b682422b9ba92ad0575c0fb4-0.parquet
    order_date=2024-06-04/34bbc317b682422b9ba92ad0575c0fb4-0.parquet
```

The folders are right, but look at the file names: pyarrow names each file with a random **unique id** plus a number (the ids above came from this run; yours will be different). That default exists so that two writers never overwrite each other's files. For a pipeline it is a trap, as section 14.4 shows. Pass `basename_template` to choose the names yourself:

```python
pq.write_to_dataset(table, "lake/orders_v2", partition_cols=["order_date"],
                    basename_template="part-{i}.parquet")
tree("lake/orders_v2")
```
```text
    order_date=2024-06-01/part-0.parquet
    order_date=2024-06-02/part-0.parquet
    order_date=2024-06-03/part-0.parquet
    order_date=2024-06-04/part-0.parquet
```

(`{i}` is replaced by a counter, in case pyarrow writes several files into one folder.)

### 14.3 Reading the whole dataset or one partition

`pq.read_table(root)` reads every partition and adds the partition column back from the folder names:

```python
everything = pq.read_table("lake/orders_v2")
print(everything.num_rows, "rows")
print(everything.schema.field("order_date"))
```
```text
7 rows
pyarrow.Field<order_date: dictionary<values=string, indices=int32, ordered=0>>
```

Note the type of `order_date`: when reading, pyarrow does not know what type the folder names were, so it **infers** one. Here it chose a dictionary-encoded string (that is what `dictionary<values=string, indices=int32>` means: each distinct value stored once, rows refer to it by number). It behaves like a string. If you want a guaranteed type, give the reader a schema or a `partitioning` object, as below.

To read **one** partition, filter on the partition column. The `pyarrow.dataset` module gives the most control:

```python
dataset = ds.dataset("lake/orders_v2", format="parquet", partitioning="hive")
print(dataset.schema.field("order_date"))
one_day = dataset.to_table(filter=ds.field("order_date") == "2024-06-03",
                           columns=["id", "status", "amount"])
print(one_day.to_pylist())
print("files in this dataset:", len(dataset.files))
```
```text
pyarrow.Field<order_date: string>
[{'id': 105, 'status': 'shipped', 'amount': Decimal('7.75')}, {'id': 106, 'status': 'pending', 'amount': Decimal('30.00')}]
files in this dataset: 4
```

With a filter on a partition column, pyarrow does not even open the files in the other folders. (The shortcut `pq.read_table(root, filters=[("order_date", "=", "2024-06-03")])` does the same thing.)

You can also read one folder directly, as an ordinary Parquet path. Then the partition column is **not** added back, because nothing tells the reader it was there:

```python
folder = pq.read_table("lake/orders_v2/order_date=2024-06-03")
print(folder.num_rows, "order_date" in folder.column_names)
```
```text
2 False
```

### 14.4 Re-running: duplicates, or replacement

What happens when the pipeline writes the same day twice, which is exactly what a re-run, a retry or a backfill does? With the default random file names, the second write adds **new** files next to the old ones, and the dataset now holds every row twice:

```python
pq.write_to_dataset(table, "lake/orders", partition_cols=["order_date"])     # a "re-run"
print(pq.read_table("lake/orders").num_rows, "rows (there are 7 orders)")
print(len(list(Path("lake/orders").rglob("*.parquet"))), "files")
```
```text
14 rows (there are 7 orders)
8 files
```

That is the CSV-append bug (Try it 24) again, in Parquet form. With fixed names (`part-{i}.parquet`) a re-run usually overwrites the same file, which looks fine until a day's data shrinks: if the first run wrote `part-0` and `part-1` and the re-run writes only `part-0`, the stale `part-1` stays behind.

The reliable answer is **`existing_data_behavior="delete_matching"`**: before writing a partition, pyarrow deletes everything already in that partition's folder. Partitions not present in the new table are left alone. That is partition replacement:

```python
def write_days(table, root):
    pq.write_to_dataset(table, root, partition_cols=["order_date"],
                        basename_template="part-{i}.parquet",
                        existing_data_behavior="delete_matching")

root = "lake/orders_v3"
write_days(table, root)
write_days(table, root)                        # re-run: same result
print(pq.read_table(root).num_rows, "rows after two runs")

# order 105 (3 June) is cancelled at the source; rewrite only 3 June
changed = [flatten_order(o) for o in ORDERS if o["id"] in (104, 105)]
changed = [r if r["id"] != 105 else {**r, "status": "cancelled"} for r in changed]
june3 = pa.Table.from_pylist([r for r in changed if r["order_date"] == "2024-06-03"], schema=ORDER_ARROW_SCHEMA)
write_days(june3, root)
print(pq.read_table(root, filters=[("order_date", "=", "2024-06-03")]).select(["id", "status"]).to_pylist())
print(pq.read_table(root).num_rows, "rows in total")
tree(root)
```
```text
7 rows after two runs
[{'id': 105, 'status': 'cancelled'}]
6 rows in total
    order_date=2024-06-01/part-0.parquet
    order_date=2024-06-02/part-0.parquet
    order_date=2024-06-03/part-0.parquet
    order_date=2024-06-04/part-0.parquet
```

Wait: 3 June now holds only order 105. Where did order 106, also placed on 3 June, go? The table we wrote for 3 June contained only the **changed** orders, and `delete_matching` replaced the **whole** folder with it. That is the most important rule of partition replacement:

> **When you replace a partition, write the complete contents of that partition, not just the changed rows.**

That is why the pipeline in section 17 rebuilds each affected day's Parquet partition from the SQLite table (which holds every current order for that day), not from the page of changes it just fetched.

```python
all_june3 = [flatten_order(o) for o in ORDERS if flatten_order(o)["order_date"] == "2024-06-03"]
all_june3 = [r if r["id"] != 105 else {**r, "status": "cancelled"} for r in all_june3]
write_days(pa.Table.from_pylist(all_june3, schema=ORDER_ARROW_SCHEMA), root)
print(pq.read_table(root, filters=[("order_date", "=", "2024-06-03")]).select(["id", "status"]).to_pylist())
print(pq.read_table(root).num_rows, "rows in total")
```
```text
[{'id': 105, 'status': 'cancelled'}, {'id': 106, 'status': 'pending'}]
7 rows in total
```

Now 3 June has both of its orders again (105 and 106; order 104 was placed on 2 June), 105 is cancelled, and the dataset has seven rows again.

**Is `delete_matching` atomic?** No. It deletes the old files, then writes the new ones. A crash in between leaves the partition empty (or half-written) until the next run. For most pipelines that is acceptable, because the next run (or the resume) rewrites the partition from the database. If readers must never see a missing day, write the new partition into a temporary folder next to it, then swap the folders: rename the old one away, rename the new one in, delete the old one. The window where the folder is missing shrinks to two renames.

### 14.5 Choosing a partition key

A good partition column:

- is used in **most filters** (analysts almost always ask for a date range, so a date is the usual choice);
- has a **moderate number of values**: hundreds or thousands of folders are fine; millions are not;
- is **stable** for a record: an order's `order_date` never changes. Partitioning by `status` would move a record to a different folder every time its status changes, and the old copy would have to be deleted from the old folder.

**Never partition by an id** or anything with one value per record. That creates one tiny file per record, which is the **small-files problem**: every file has fixed overhead (opening it, reading its footer, a listing call on cloud storage), so a dataset of 100,000 files of 2 KB is far slower to read than 10 files of 20 MB, even though the data is the same. Rough guidance: aim for files of tens to hundreds of megabytes. A shop with 300 orders a day might partition by **month** instead of day; a shop with millions might partition by day and even split days into several files.

Some datasets use several levels, `year=2024/month=06/day=03/`, which lets readers prune by year or month cheaply. One level by date (`order_date=2024-06-03`) is simpler and enough for most pipelines.

### 14.6 Try it: partitioning

**Try it 33.** An orders table has rows for 2024-06-01 (2 rows), 2024-06-02 (1 row) and 2024-06-03 (3 rows). You write it with `partition_cols=["order_date"]`, `basename_template="part-{i}.parquet"`, `existing_data_behavior="delete_matching"`. Then you write a second table containing 2 rows for 2024-06-03 and 1 row for 2024-06-04, the same way. How many folders and how many rows are there, and how many rows are in 2024-06-03?

<details><summary>Answer</summary>

```python
import pyarrow.dataset as ds
from pathlib import Path

def write(rows, root):
    t = pa.table({"id": [r[0] for r in rows], "order_date": [r[1] for r in rows]})
    pq.write_to_dataset(t, root, partition_cols=["order_date"], basename_template="part-{i}.parquet",
                        existing_data_behavior="delete_matching")

root = "lake/try33"
write([(1, "2024-06-01"), (2, "2024-06-01"), (3, "2024-06-02"),
       (4, "2024-06-03"), (5, "2024-06-03"), (6, "2024-06-03")], root)
write([(7, "2024-06-03"), (8, "2024-06-03"), (9, "2024-06-04")], root)
print(sorted(p.name for p in Path(root).iterdir()))
everything = pq.read_table(root)
print(everything.num_rows, "rows;", "2024-06-03 ids:",
      pq.read_table(root, filters=[("order_date", "=", "2024-06-03")]).column("id").to_pylist())
```
```text
['order_date=2024-06-01', 'order_date=2024-06-02', 'order_date=2024-06-03', 'order_date=2024-06-04']
6 rows; 2024-06-03 ids: [7, 8]
```

Four folders. 2024-06-01 and 2024-06-02 were not in the second table, so they were left alone (3 rows). 2024-06-03 was **replaced** by the 2 new rows (ids 7 and 8; ids 4 to 6 are gone). 2024-06-04 is new (1 row). Total: 6 rows.

</details>

**Try it 34.** Suggest a partition column (or none) for each, with a reason: (a) 20 million web events per day, analysed by day; (b) a book catalogue of 5,000 rows, fully reloaded every night; (c) orders, about 50 per day, kept for 5 years.

<details><summary>Answer</summary>

(a) **By event date** (`event_date=...`): large daily volume, every query filters by date; each day may even be split into several files. (b) **None**: 5,000 rows fit in one small file; partitioning would only create tiny files; a full reload replaces the single file atomically. (c) **By month** (`order_month=2024-06`) or even by year: daily partitions would hold 50 rows each (about 1,800 tiny files over 5 years); monthly gives 60 files of about 1,500 rows, still small but far fewer.

</details>

## 15. Schema evolution

### 15.1 Schemas change

The API you built for in January is not the API you have in June. The order service adds a field (`gift_wrap`), stops sending one (`currency` because every order is in INR now), renames one (`amount` to `total`), or changes a type (`id` from a number to a string like `"ORD-101"`). **Schema evolution** is how a pipeline copes with those changes without losing data or breaking readers.

The changes are not equally dangerous:

| Change | Example | Danger | Usual response |
|---|---|---|---|
| **Add an optional field** | `gift_wrap: true` appears | low | tolerate it; add a nullable column when you need it |
| **Remove a field** | `currency` disappears | medium | if required by your contract, records fail validation; decide a default or relax the contract |
| **Rename a field** | `amount` becomes `total` | high | looks like "remove + add": every record fails, or worse, loads with nulls |
| **Change a type** | `id`: `101` becomes `"ORD-101"` | high | schema check fails; needs a migration |
| **Change meaning** | `amount` now includes tax | highest | no check can see it; only communication catches it |

The last row is a reminder that schema checks are not enough on their own. Talk to the team that owns the source, and ask to be told about changes **before** they ship.

### 15.2 Tolerant reading, strict writing

A pipeline survives most additions if it follows one principle: **be tolerant in what you read, strict in what you write**.

- **Reading**: ignore unknown fields (the schema checker in section 6.1 does). Keep the raw record (section 4.3), so a field you ignored today can be used later by replaying.
- **Writing**: write only the columns your output schema declares, with their declared types. Never let whatever the API happened to send decide the shape of your tables.

Then an added field changes nothing until **you** decide to add it to the output.

### 15.3 Adding a column in SQLite

When you decide to keep the new field, the SQLite table needs a new column. `ALTER TABLE ... ADD COLUMN` adds a column to an existing table; existing rows get `NULL` (or the column's default). The pipeline can check which columns exist (`PRAGMA table_info`) and add any that are missing, so the change is applied automatically and safely on the next run:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
con.executemany("INSERT INTO orders VALUES (?, ?)", [(101, "shipped"), (102, "pending")])

WANTED_COLUMNS = {"id": "INTEGER", "status": "TEXT", "gift_wrap": "INTEGER"}

def add_missing_columns(con, table, wanted):
    existing = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
    added = []
    for name, sql_type in wanted.items():
        if name not in existing:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}")
            added.append(name)
    return added

print("added:", add_missing_columns(con, "orders", WANTED_COLUMNS))
print("added on a second run:", add_missing_columns(con, "orders", WANTED_COLUMNS))
con.execute("INSERT INTO orders VALUES (103, 'shipped', 1)")
print(con.execute("SELECT * FROM orders ORDER BY id").fetchall())
```
```text
added: ['gift_wrap']
added on a second run: []
[(101, 'shipped', None), (102, 'pending', None), (103, 'shipped', 1)]
```

Old rows have `gift_wrap = None`, which honestly means "we do not know" (the field did not exist when they were loaded); new rows have a value. Running `add_missing_columns` a second time adds nothing: it is idempotent, so it can run at the start of every pipeline run.

(The table and column names are put into the SQL with an f-string because SQL parameters (`?`) cannot be used for names. That is only safe because the names come from **our own** constant `WANTED_COLUMNS`, never from the API. This is the allow-list rule from the last chapter.)

### 15.4 Old and new Parquet files together

Parquet files are written once and never changed. After the API adds `gift_wrap`, old files do not have the column and new files do. What happens when you read them together?

```python
from pathlib import Path
import pyarrow.dataset as ds

Path("evolve").mkdir()
old = pa.table({"id": [101, 102], "status": ["shipped", "pending"]})
new = pa.table({"id": [103], "status": ["shipped"], "gift_wrap": [True]})
pq.write_table(old, "evolve/part-2024-06-01.parquet")
pq.write_table(new, "evolve/part-2024-06-02.parquet")

naive = pq.read_table("evolve")
print(naive.column_names, naive.num_rows)
```
```text
['id', 'status'] 3
```

The column `gift_wrap` is **gone**. When a dataset has files with different schemas, pyarrow uses the schema of the **first** file it finds, and drops columns the others have. No error, no warning, just silently missing data. (If the new file had happened to sort first, you would get the column, so the result depends on file names. That is an even better reason not to rely on the default.)

The fix is to **unify** the schemas: build one schema that contains every column from every file, and read with it. `pa.unify_schemas` does that, and columns missing from a file are filled with nulls:

```python
schemas = [pq.read_schema(path) for path in sorted(Path("evolve").glob("*.parquet"))]
unified = pa.unify_schemas(schemas)
print(unified)
dataset = ds.dataset("evolve", format="parquet", schema=unified)
print(dataset.to_table().sort_by("id").to_pylist())
```
```text
id: int64
status: string
gift_wrap: bool
[{'id': 101, 'status': 'shipped', 'gift_wrap': None}, {'id': 102, 'status': 'pending', 'gift_wrap': None}, {'id': 103, 'status': 'shipped', 'gift_wrap': True}]
```

If you already have the tables in memory, `pa.concat_tables(tables, promote_options="default")` does the same job: it adds missing columns as nulls.

```python
print(pa.concat_tables([old, new], promote_options="default").to_pylist())
```
```text
[{'id': 101, 'status': 'shipped', 'gift_wrap': None}, {'id': 102, 'status': 'pending', 'gift_wrap': None}, {'id': 103, 'status': 'shipped', 'gift_wrap': True}]
```

In a pipeline you do not want to discover the schema from whatever files exist. You want **one declared schema per version**: when you add `gift_wrap`, you add it to the pipeline's `pa.schema([...])` as a nullable field, and readers use that schema. The unify trick is for reading data you did not write, or data written before you were careful.

### 15.5 Type changes and renames need a migration

Unifying works when columns are **added**. It cannot merge two different types for the same column:

```python
try:
    pa.unify_schemas([pa.schema([("id", pa.int64())]), pa.schema([("id", pa.string())])])
except pa.ArrowTypeError as error:
    print("ArrowTypeError:", error)
```
```text
ArrowTypeError: Unable to merge: Field id has incompatible types: int64 vs string
```

A type change or a rename needs a deliberate **migration**:

1. Decide the new schema (for example, `id` becomes a string everywhere).
2. Rewrite the old data to the new schema: read each old partition, cast or rename the column, write it back (with partition replacement, so it is safe to re-run).
3. Switch the pipeline to the new schema.
4. For SQLite, create a new table with the new definition, copy the rows across with `INSERT INTO new SELECT ...`, and rename the tables, all in one transaction.

A **rename** is safest as a two-step change: add the new column (filled from the old one), keep writing both for a while so readers can switch, then remove the old column. Never just "start writing `total` instead of `amount`": every reader that asks for `amount` silently gets nulls from the new files.

### 15.6 Try it: schema evolution

**Try it 35.** The API starts sending `"coupon": "SUMMER10"` on some orders. Walk through what happens, step by step, in a pipeline built like this chapter's (tolerant schema check, raw layer, explicit Arrow schema), before you change any code. Then list the changes needed to keep the coupon in SQLite and Parquet.

<details><summary>Answer</summary>

Before any change: `check_schema` ignores the unknown field, so no record is quarantined; the raw layer stores the full JSON including `coupon`; `flatten_order` does not copy it, and the explicit Arrow schema has no `coupon` column, so the SQLite and Parquet outputs are unchanged. Nothing breaks, and nothing is lost, because the raw layer has it.

To keep it: (1) add `coupon` (nullable) to the flatten step; (2) add it to `WANTED_COLUMNS` so `add_missing_columns` creates `coupon TEXT` in SQLite on the next run; (3) add `pa.field("coupon", pa.string())` to the Arrow schema; (4) optionally **backfill**: rebuild past rows and partitions from the raw layer, so older orders that had coupons get them (orders from before the API change stay null, meaning "unknown"); (5) tell readers that new files have the column, and read mixed files with the declared (or unified) schema so it is not silently dropped.

</details>

## 16. Sensitive data

### 16.1 What counts as sensitive

A pipeline copies data to places where more people can see it. That makes it the place where privacy is won or lost. **Personal data** (often called **PII**, personally identifiable information) is any information about an identifiable person: names, email addresses, phone numbers, postal addresses, government ids, payment details, IP addresses, precise locations.

Two less obvious kinds matter too:

- **Quasi-identifiers**: fields that are harmless alone but identify a person in combination. "Pune, ordered at 10:02 on 1 June, bought 2 copies of B1" may point to exactly one person.
- **Secrets**: API tokens, passwords, keys. Not personal data, but leaking them gives an attacker access to everything else.

Many countries have laws about personal data (the GDPR in Europe, India's Digital Personal Data Protection Act of 2023, and others). The details belong to lawyers, but the engineering habits that keep you on the right side of them are the same everywhere, and they are the subject of this section: **collect less, keep less, show less, protect secrets, and delete on time**.

### 16.2 Data minimisation: an allow-list of columns

The safest personal data is data you never copied. Before any output is written, decide which columns each output needs, and keep **only** those. Use an **allow-list** (the columns you may keep), never a deny-list (the columns you must drop):

```python
ALLOWED = {"id", "status", "amount", "order_date", "customer_city"}

def minimise(row, allowed=ALLOWED):
    return {k: v for k, v in row.items() if k in allowed}

row = flatten_order(ORDERS[0])
row["customer_phone"] = "+91 98765 43210"          # a field the API added last week
print(sorted(row))
print(minimise(row))
```
```text
['amount', 'created_at', 'currency', 'customer_city', 'customer_email', 'customer_phone', 'id', 'item_lines', 'order_date', 'qty_total', 'status', 'updated_at']
{'id': 101, 'customer_city': 'Pune', 'status': 'shipped', 'amount': Decimal('19.99'), 'order_date': '2024-06-01'}
```

With a deny-list ("drop `customer_email`"), the new `customer_phone` field would have flowed into every output without anyone deciding it should. An allow-list fails **safe**: a new field is dropped until someone deliberately adds it.

### 16.3 Masking

**Masking** hides most of a value but keeps enough for a person to recognise it, for example on a support screen: `a***@example.com`. It is for display, not for analysis: masked values are not unique (`a***@example.com` could be Asha or Arjun).

```python
def mask_email(email):
    if not isinstance(email, str) or email.count("@") != 1:
        return None                                   # not an email: show nothing rather than leak it
    local, domain = email.split("@")
    if not local or not domain:
        return None
    return f"{local[0]}***@{domain}"
```

```python
for value in ["asha@example.com", "b@example.com", "not-an-email", "x@y@z", None]:
    print(repr(value), "->", repr(mask_email(value)))
```
```text
'asha@example.com' -> 'a***@example.com'
'b@example.com' -> 'b***@example.com'
'not-an-email' -> None
'x@y@z' -> None
None -> None
```

Note the edge cases. A one-letter name still becomes `b***` (so the mask does not reveal the length), and anything that does not look like an email returns `None` rather than being shown unmasked "because the function did not understand it". When a privacy function is unsure, it should hide, not show.

### 16.4 Pseudonymisation with HMAC

Analysts often need to **count and join by customer** ("how many customers ordered twice?") without knowing who the customers are. Masking cannot do that. **Pseudonymisation** replaces the email with a stable token: the same email always gives the same token, so counts and joins still work, but the token does not reveal the email.

The obvious idea, a plain hash, is not good enough:

```python
import hashlib

def sha_token(email):
    return hashlib.sha256(email.encode()).hexdigest()[:16]

leaked_tokens = {sha_token(o["customer"]["email"]) for o in ORDERS}

# An attacker with a list of known email addresses (from another leak, a mailing list...):
known_emails = ["ravi@example.com", "asha@example.com", "chen@example.com", "zoe@example.com"]
cracked = {sha_token(e): e for e in known_emails if sha_token(e) in leaked_tokens}
print("re-identified:", sorted(cracked.values()))
```
```text
re-identified: ['asha@example.com', 'chen@example.com']
```

SHA-256 is public and has no secret, so anyone can hash a list of candidate emails and compare. That is a **dictionary attack**, and emails are easy to guess in bulk. The fix is a **keyed** hash: **HMAC** (Hash-based Message Authentication Code) mixes a secret key into the hash. Without the key, an attacker cannot compute tokens for their candidate list, so the dictionary attack fails.

```python
import hashlib
import hmac

def pseudonymise(email, key: bytes):
    normalised = email.strip().lower().encode("utf-8")
    return hmac.new(key, normalised, hashlib.sha256).hexdigest()[:16]
```

```python
key = b"example-key-for-this-chapter-only"
print(pseudonymise("asha@example.com", key))
print(pseudonymise("  ASHA@example.com ", key))          # same person, same token
print(pseudonymise("asha@example.com", b"another-key"))  # different key, different token
tokens = {pseudonymise(o["customer"]["email"], key) for o in ORDERS}
print(len(ORDERS), "orders,", len(tokens), "distinct customers")
print("attacker without the key cracks:", [e for e in known_emails if sha_token(e) in tokens])
```
```text
4604d5f6851e5a52
4604d5f6851e5a52
0c1fd3ffad598fc4
7 orders, 6 distinct customers
attacker without the key cracks: []
```

Asha's two orders get the same token, so "distinct customers" is 6 for 7 orders. Normalising first (strip, lowercase) makes `ASHA@example.com` and `asha@example.com` the same person. And the attacker's list matches nothing.

(We keep the first 16 hex characters, 64 bits, which is plenty to avoid accidental collisions for millions of customers and shorter to store. Keep the full 64 characters if in doubt.)

Important facts about pseudonymised data:

- It is **not anonymous**. Whoever has the key can recompute tokens for known emails and re-identify people, so most laws still treat it as personal data. It reduces risk; it does not remove the duty to protect the data.
- **The key is now the crown jewel.** Anyone with it can reverse the protection for guessable values. It is a secret, handled like a password (next section).
- **Changing the key changes every token.** Joins between data made with the old key and the new key break. Plan key rotation as a migration, not a casual change.

### 16.5 Secrets: never in code, never in logs

The HMAC key, API tokens and database passwords are **secrets**. Three rules:

1. **Never in code or in git.** Code is copied, shared, and kept for ever in version control history. A token committed once is leaked, even if you delete it in the next commit.
2. **Read them from the environment** (or a secrets manager in bigger setups). The program reads `os.environ["PAGEBOUND_PSEUDO_KEY"]`; the value is set outside the program, in the shell, the scheduler, or a `.env` file that is listed in `.gitignore`.
3. **Fail clearly when one is missing**, and **never print or log it**, not even in an error message.

```python
import os
from dataclasses import dataclass, field

class MissingSecret(RuntimeError):
    pass

def require_secret(name, env=os.environ):
    value = env.get(name, "").strip()
    if not value:
        raise MissingSecret(f"environment variable {name} is not set. "
                            f"Set it before running (see config.example.toml); it must not be committed.")
    return value

@dataclass(frozen=True)
class Settings:
    base_url: str
    api_token: str = field(repr=False)                # repr=False: never shown when printed or logged
    pseudo_key: bytes = field(repr=False)

try:
    require_secret("PAGEBOUND_API_TOKEN", env={})
except MissingSecret as error:
    print(error)

fake_env = {"PAGEBOUND_API_TOKEN": "tok_example_123", "PAGEBOUND_PSEUDO_KEY": "example-key"}
settings = Settings("https://api.pagebound.test",
                    api_token=require_secret("PAGEBOUND_API_TOKEN", fake_env),
                    pseudo_key=require_secret("PAGEBOUND_PSEUDO_KEY", fake_env).encode())
print(settings)
```
```text
environment variable PAGEBOUND_API_TOKEN is not set. Set it before running (see config.example.toml); it must not be committed.
Settings(base_url='https://api.pagebound.test')
```

`field(repr=False)` keeps the secret out of the dataclass's printed form, so `log.info("config: %s", settings)` is safe. The error for a missing secret says **which** variable and **where** to look, and never contains a value. Passing `env` as an argument (defaulting to `os.environ`) is the same injection idea as before: tests pass a small dict instead of changing the real environment. (With pytest, `monkeypatch.setenv(...)` and `monkeypatch.delenv(...)` are the other clean way.)

Send API tokens in a **header** (`Authorization: Bearer ...`), never in the URL, because URLs end up in logs, browser histories and proxy logs (section 12.6).

### 16.6 Least privilege: each reader sees only what it needs

**Least privilege** means every person and program gets the minimum access its job needs. For pipeline outputs, that means different **views** of the data for different roles:

| Role | Needs | Should not see |
|---|---|---|
| finance | order ids, amounts, dates, statuses | who the customer is |
| support | one order's status, a masked email to confirm with the caller | full emails of everyone |
| analysts | customer tokens for counting and joining, city, amounts | emails at all |
| the pipeline itself | everything it processes | (it is the one place the raw data exists) |

Real databases (PostgreSQL, MySQL) enforce this with users, roles and `GRANT`: you create a view per role and grant each role `SELECT` on its view only. SQLite has no users (anyone who can open the file can read all of it), but views still show the **shape** of each role's access, and the same SQL moves to a real database later:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.create_function("mask_email", 1, mask_email)              # a Python function callable from SQL
con.execute("""CREATE TABLE orders_private (
    id INTEGER PRIMARY KEY, email TEXT, customer_key TEXT, city TEXT, status TEXT, amount_cents INTEGER)""")
key = b"example-key-for-this-chapter-only"
con.executemany("INSERT INTO orders_private VALUES (?, ?, ?, ?, ?, ?)",
                [(o["id"], o["customer"]["email"], pseudonymise(o["customer"]["email"], key),
                  o["customer"]["city"], o["status"], int(Decimal(o["amount"]) * 100)) for o in ORDERS[:3]])

con.executescript("""
CREATE VIEW finance_orders AS SELECT id, status, amount_cents FROM orders_private;
CREATE VIEW support_orders AS SELECT id, status, mask_email(email) AS email_hint FROM orders_private;
CREATE VIEW analyst_orders AS SELECT id, customer_key, city, amount_cents FROM orders_private;
""")
for view in ["finance_orders", "support_orders", "analyst_orders"]:
    cursor = con.execute(f"SELECT * FROM {view} WHERE id = 101")
    print(f"{view:15}", [d[0] for d in cursor.description], cursor.fetchone())
```
```text
finance_orders  ['id', 'status', 'amount_cents'] (101, 'shipped', 1999)
support_orders  ['id', 'status', 'email_hint'] (101, 'shipped', 'a***@example.com')
analyst_orders  ['id', 'customer_key', 'city', 'amount_cents'] (101, '4604d5f6851e5a52', 'Pune', 1999)
```

(`con.create_function` registers `mask_email` so SQL can call it. In a real database you would write the masking in SQL, since other programs reading the view would not have your Python function.)

For **files**, least privilege means file permissions. On Linux and macOS, `os.chmod(path, 0o600)` makes a file readable and writable by its owner only:

```python
import os
import stat
from pathlib import Path

secret_file = Path("quarantine.jsonl")
secret_file.write_text("{}\n", encoding="utf-8")
os.chmod(secret_file, 0o600)
print(stat.filemode(secret_file.stat().st_mode))      # Linux output; Windows shows something different
```
```text
-rw-------
```

`-rw-------` means: owner can read and write; group and others can do nothing. On Windows, `os.chmod` can only set or clear the read-only flag; real access control there is done with folder permissions (ACLs), set by an administrator or with Windows tools. Either way, the principle is the same: the quarantine file, the raw layer and the checkpoint (which may contain personal data) should be readable only by the pipeline's own account.

### 16.7 Retention: delete on time

Data you keep for ever is data that can leak for ever. Every dataset the pipeline writes should have a **retention period**, written down, and the pipeline (or a separate cleanup job) should enforce it:

- **raw layer**: long enough to replay recent fixes, for example 30 days;
- **quarantine**: until each record is fixed and replayed, and at most, say, 30 days;
- **clean tables and Parquet**: as long as the business needs them, often years, but **without** direct identifiers (pseudonymised or dropped);
- **logs**: days to weeks, and they should contain no personal data anyway.

With date-partitioned data, retention is simple and cheap:

```python
import shutil
from datetime import date, timedelta
from pathlib import Path

root = Path("lake/raw_orders")
for day in ["2024-04-20", "2024-05-06", "2024-05-07", "2024-06-01"]:
    (root / f"fetch_date={day}").mkdir(parents=True)
    (root / f"fetch_date={day}" / "part-0.parquet").write_bytes(b"(pretend parquet)")

def apply_retention(root, today, keep_days):
    cutoff = today - timedelta(days=keep_days)
    removed = []
    for folder in sorted(root.glob("fetch_date=*")):
        day = date.fromisoformat(folder.name.split("=", 1)[1])
        if day < cutoff:
            shutil.rmtree(folder)
            removed.append(folder.name)
    return cutoff, removed

print(apply_retention(root, today=date(2024, 6, 5), keep_days=30))
print(sorted(p.name for p in root.iterdir()))
```
```text
(datetime.date(2024, 5, 6), ['fetch_date=2024-04-20'])
['fetch_date=2024-05-06', 'fetch_date=2024-05-07', 'fetch_date=2024-06-01']
```

In SQLite the same rule is a `DELETE ... WHERE fetched_at < ?`. Make the retention job idempotent too (running it twice removes nothing more), and log how much it removed, not what.

### 16.8 A checklist for every new pipeline

Before a pipeline goes live, answer these questions in writing:

1. Which personal fields does the source send? Which do we **need**?
2. Which fields are dropped (allow-list), masked, or pseudonymised in each output?
3. Where is the pseudonymisation key kept, who can read it, and how would we rotate it?
4. Where are secrets stored? Are any in code, config files in git, URLs or logs?
5. Who can read the raw layer, the quarantine, the checkpoint, the logs? (They contain the most.)
6. What is the retention period for each dataset, and what deletes the data on time?

### 16.9 Try it: sensitive data

**Try it 36.** Your teammate pseudonymises with `hashlib.sha256(email.encode()).hexdigest()` and says "it is a one-way hash, nobody can reverse it". What is wrong with the argument, and what two changes would you make?

<details><summary>Answer</summary>

"One-way" means you cannot compute the email **from** the hash, but an attacker does not need to: they compute hashes **of** guessed emails and look for matches (section 16.4 re-identified two customers this way). Emails are guessable in bulk. Changes: (1) use **HMAC-SHA256 with a secret key** read from the environment, so tokens cannot be computed without the key; (2) **normalise** the email (strip, lowercase) before hashing, so the same person always gets the same token. Also keep the key out of code, logs and the data itself, and remember that pseudonymised data still counts as personal data.

</details>

**Try it 37.** Predict exactly what each role sees for order 102 (whose city is `null`) using the three views in section 16.6. Then say which view a support agent should use, and why not `analyst_orders`.

<details><summary>Answer</summary>

```python
for view in ["finance_orders", "support_orders", "analyst_orders"]:
    print(f"{view:15}", con.execute(f"SELECT * FROM {view} WHERE id = 102").fetchone())
```
```text
finance_orders  (102, 'pending', 550)
support_orders  (102, 'pending', 'b***@example.com')
analyst_orders  (102, 'a0162f8efa0b4090', None, 550)
```

Finance sees `(102, 'pending', 550)`; support sees `(102, 'pending', 'b***@example.com')`; analysts see the id, a 16-character token, `None` for the city, and 550. A support agent uses `support_orders`: the email hint lets them confirm "is your email b-something at example.com?" without seeing the address. The analyst view would not help them (a token means nothing to a caller), and it exposes more than support needs, because tokens let you link all of one customer's orders together.

</details>

**Try it 38.** Find the problems: a pipeline's `config.toml` (committed to git) contains `api_token = "tok_live_9f8e..."`, and the pipeline logs `log.info("calling %s", f"{base_url}/v1/orders?token={api_token}")`.

<details><summary>Answer</summary>

Three leaks. (1) The token is **committed to git**: everyone with access to the repository, and every clone and backup, now has it, and deleting the line later does not remove it from history. It must be **revoked** and replaced, and the new one read from an environment variable. (2) The token is **in the URL**, so it is stored by proxies, server logs and httpx's own debug logging; send it in an `Authorization` header instead. (3) The pipeline **logs the URL with the token**. Log the path and the parameters that are not secret, never credentials. A good repository has `config.example.toml` with empty secret values and `config.toml` in `.gitignore`.

</details>

## 17. Putting it together

### 17.1 The shape of a pipeline module

Sixteen sections, sixteen techniques. A real pipeline uses most of them at once, and the hard part is arranging them so the code stays readable. A good arrangement has one small function or group of functions per stage, and one `run()` function that tells the story in order:

```text
pipeline.py
├── configuration   Config dataclass; load_config() reads paths and secrets (from the environment)
├── extract         get_with_retry(): one GET with retries and backoff
├── transform       validate() -> list of reasons;  transform() -> flat typed row (pure)
├── load            upsert() into SQLite (only if newer);  publish_partitions() to Parquet
├── state           checkpoint file (atomic);  watermark in SQLite
└── run()           the story: resume or start -> pages -> quarantine/load -> publish -> watermark -> summary
```

Rules that keep it testable:

- **Every outside dependency is a parameter**: the `client`, the clock (`now`), `sleep`, `rand`, the environment, the folder to write in. Tests pass fakes; production passes the real things.
- **The transform is pure.** No I/O, no clock.
- **`run()` returns its statistics** (and logs them), so tests can assert counts without parsing logs.

### 17.2 The whole pipeline

Here is a complete pipeline in one file, about 200 lines. It fetches the Pagebound Orders API incrementally with an overlap window; retries transient errors with backoff and jitter; validates every record and quarantines bad ones; pseudonymises the customer's email with HMAC (the email itself is never stored); upserts into SQLite only if newer; saves a checkpoint after every page so a crash can resume; rebuilds the Parquet partition of every day it touched; moves the watermark only at the very end; and logs a one-line summary. Everything in it is something you have already seen in this chapter.

```python
"""Incremental, resumable pipeline: Pagebound Orders API -> SQLite (upsert) + partitioned Parquet."""
import hashlib
import hmac
import json
import logging
import os
import random
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx
import pyarrow as pa
import pyarrow.parquet as pq

log = logging.getLogger("pipeline")
IST = timezone(timedelta(hours=5, minutes=30), "IST")
STATUSES = {"shipped", "pending", "cancelled"}
RETRY_STATUS = {429, 500, 502, 503, 504}

# ---------------------------------------------------------------- configuration
@dataclass(frozen=True)
class Config:
    db_path: Path
    parquet_root: Path
    state_dir: Path
    pseudo_key: bytes = field(repr=False)          # a secret: never printed
    per_page: int = 3
    max_pages: int = 1000
    overlap: timedelta = timedelta(minutes=10)
    max_attempts: int = 4
    max_bad_fraction: float = 0.05
    min_records_for_fraction: int = 20

def load_config(base_dir, env=os.environ):
    key = env.get("PAGEBOUND_PSEUDO_KEY", "").strip()
    if not key:
        raise RuntimeError("PAGEBOUND_PSEUDO_KEY is not set (see config.example.toml)")
    base_dir = Path(base_dir)
    return Config(db_path=base_dir / "orders.db", parquet_root=base_dir / "parquet",
                  state_dir=base_dir / "state", pseudo_key=key.encode("utf-8"))

# ---------------------------------------------------------------- extract
def get_with_retry(client, params, cfg, sleep, rand):
    """GET /v1/orders with retries for transport errors, 429 and 5xx. Returns the JSON body."""
    for attempt in range(cfg.max_attempts):
        last = attempt == cfg.max_attempts - 1
        backoff = min(30.0, 0.5 * 2 ** attempt)
        delay = backoff / 2 + rand() * backoff / 2                  # equal jitter
        try:
            response = client.get("/v1/orders", params=params)
        except httpx.TransportError as error:
            if last:
                raise
            reason = type(error).__name__
        else:
            if response.status_code not in RETRY_STATUS:
                return response.raise_for_status().json()
            if last:
                response.raise_for_status()
            reason = str(response.status_code)
            retry_after = response.headers.get("Retry-After", "")
            if retry_after.isdigit():
                delay = min(float(retry_after), 30.0)              # exactly as asked, but capped
        log.warning("page %s attempt %d failed (%s); retrying in %.2fs",
                    params.get("page"), attempt + 1, reason, delay)
        sleep(delay)

# ---------------------------------------------------------------- transform
REQUIRED = {"id": int, "customer": dict, "status": str, "amount": str,
            "created_at": str, "updated_at": str, "items": list}

def parse_ts(text):
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise ValueError(f"no time zone in {text!r}")
    return value.astimezone(timezone.utc)

def validate(record):
    """Return a list of reasons why the record is bad (empty list = good)."""
    if not isinstance(record, dict):
        return ["record: not an object"]
    errors = [f"{name}: missing, null or not {kind.__name__}"
              for name, kind in REQUIRED.items()
              if isinstance(record.get(name), bool) or not isinstance(record.get(name), kind)]
    if errors:
        return errors
    try:
        amount = Decimal(record["amount"])
        if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
            errors.append("amount: not a non-negative value with 2 decimals")
    except InvalidOperation:
        errors.append("amount: not a number")
    if record["status"] not in STATUSES:
        errors.append(f"status: unknown value {record['status']!r}")
    for name in ("created_at", "updated_at"):
        try:
            parse_ts(record[name])
        except ValueError:
            errors.append(f"{name}: not an ISO timestamp with a time zone")
    if not isinstance(record["customer"].get("email"), str):
        errors.append("customer.email: missing")
    if any(not isinstance(i, dict) or type(i.get("qty")) is not int for i in record["items"]):
        errors.append("items: every item needs an integer qty")
    return errors

def pseudonymise(email, key):
    return hmac.new(key, email.strip().lower().encode("utf-8"), hashlib.sha256).hexdigest()[:16]

def transform(record, key):
    """Pure: a valid API record -> a flat row. The email is replaced by a keyed token."""
    created = parse_ts(record["created_at"])
    city = record["customer"].get("city")
    return {
        "id": record["id"],
        "customer_key": pseudonymise(record["customer"]["email"], key),
        "city": (" ".join(city.split()).title() or None) if isinstance(city, str) else None,
        "status": record["status"],
        "amount_cents": int(Decimal(record["amount"]) * 100),
        "order_date": created.astimezone(IST).date().isoformat(),
        "created_at": created.isoformat(),
        "updated_at": parse_ts(record["updated_at"]).isoformat(),
        "qty_total": sum(item["qty"] for item in record["items"]),
    }

# ---------------------------------------------------------------- load
COLUMNS = ["id", "customer_key", "city", "status", "amount_cents", "order_date",
           "created_at", "updated_at", "qty_total"]
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY, customer_key TEXT NOT NULL, city TEXT, status TEXT NOT NULL,
    amount_cents INTEGER NOT NULL, order_date TEXT NOT NULL, created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL, qty_total INTEGER NOT NULL, last_run TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pipeline_state (name TEXT PRIMARY KEY, value TEXT);
"""
UPSERT_SQL = f"""
INSERT INTO orders ({", ".join(COLUMNS)}, last_run) VALUES ({", ".join("?" * (len(COLUMNS) + 1))})
ON CONFLICT(id) DO UPDATE SET {", ".join(f"{c} = excluded.{c}" for c in COLUMNS[1:])},
    last_run = excluded.last_run
WHERE excluded.updated_at > orders.updated_at
"""
PARQUET_SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("customer_key", pa.string(), nullable=False),
    pa.field("city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(12, 2), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("updated_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("qty_total", pa.int64(), nullable=False),
    pa.field("order_date", pa.string(), nullable=False),
])

def upsert(con, rows, run_id):
    before = con.total_changes
    con.executemany(UPSERT_SQL, [[row[c] for c in COLUMNS] + [run_id] for row in rows])
    return con.total_changes - before

def publish_partitions(con, root, days):
    """Rewrite each day's Parquet partition from ALL of that day's rows in SQLite."""
    for day in days:
        rows = con.execute(f"SELECT {', '.join(COLUMNS)} FROM orders WHERE order_date = ? ORDER BY id",
                           (day,)).fetchall()
        records = [dict(zip(COLUMNS, row)) for row in rows]
        for r in records:
            r["amount"] = Decimal(r.pop("amount_cents")) / 100
            r["created_at"] = datetime.fromisoformat(r["created_at"])
            r["updated_at"] = datetime.fromisoformat(r["updated_at"])
        table = pa.Table.from_pylist(records, schema=PARQUET_SCHEMA)
        pq.write_to_dataset(table, root, partition_cols=["order_date"],
                            basename_template="part-{i}.parquet", existing_data_behavior="delete_matching")

# ---------------------------------------------------------------- state
def write_json_atomic(path, data):
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def load_checkpoint(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None

def get_state(con, name):
    row = con.execute("SELECT value FROM pipeline_state WHERE name = ?", (name,)).fetchone()
    return row[0] if row else None

# ---------------------------------------------------------------- run
class TooManyBadRecords(Exception):
    pass

def run(client, cfg, *, now=lambda: datetime.now(timezone.utc), sleep=time.sleep,
        rand=random.random, new_run_id=None):
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = cfg.state_dir / "checkpoint.json"
    quarantine_path = cfg.state_dir / "quarantine.jsonl"
    stats = {"pages": 0, "fetched": 0, "written": 0, "quarantined": 0, "days": 0}
    started = time.perf_counter()
    run_id = "?"
    con = sqlite3.connect(cfg.db_path)
    try:
        con.executescript(SCHEMA_SQL)
        state = load_checkpoint(checkpoint_path)
        if state is not None and not state["done"]:                       # resume
            run_id, since, page = state["run_id"], state["since"], state["next_page"]
            log.info("run %s: resuming at page %s", run_id, page)
        else:                                                              # fresh run
            run_id = new_run_id or now().strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
            watermark = get_state(con, "watermark")
            since = None
            if watermark is not None:
                since = (parse_ts(watermark) - cfg.overlap).strftime("%Y-%m-%dT%H:%M:%SZ")
            page = 1
            log.info("run %s: starting, updated_since=%s", run_id, since)

        while page is not None:
            if stats["pages"] == cfg.max_pages:
                raise RuntimeError(f"more than {cfg.max_pages} pages; is the API looping?")
            params = {"page": page, "per_page": cfg.per_page}
            if since is not None:
                params["updated_since"] = since
            body = get_with_retry(client, params, cfg, sleep, rand)
            good = []
            for record in body["data"]:
                reasons = validate(record)
                if reasons:
                    record_id = record.get("id") if isinstance(record, dict) else None
                    with quarantine_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({"run_id": run_id, "id": record_id, "reasons": reasons,
                                            "record": record}, sort_keys=True) + "\n")
                    log.warning("order %s quarantined: %s", record_id, "; ".join(reasons))
                    stats["quarantined"] += 1
                else:
                    good.append(transform(record, cfg.pseudo_key))
            with con:                                                      # 1. data
                stats["written"] += upsert(con, good, run_id)
            stats["pages"] += 1
            stats["fetched"] += len(body["data"])
            page = body["next_page"]
            write_json_atomic(checkpoint_path, {"run_id": run_id, "since": since,   # 2. checkpoint
                                                "next_page": page, "done": False})

        total, bad = stats["fetched"], stats["quarantined"]
        if (total >= cfg.min_records_for_fraction and bad / total > cfg.max_bad_fraction) or \
           (total < cfg.min_records_for_fraction and bad > max(1, int(total * cfg.max_bad_fraction))):
            raise TooManyBadRecords(f"{bad} of {total} records were bad; watermark not moved")

        days = [r[0] for r in con.execute(
            "SELECT DISTINCT order_date FROM orders WHERE last_run = ? ORDER BY 1", (run_id,))]
        publish_partitions(con, cfg.parquet_root, days)
        stats["days"] = len(days)
        with con:                                                          # 3. watermark last
            newest = con.execute("SELECT MAX(updated_at) FROM orders").fetchone()[0]
            if newest is not None:
                con.execute("INSERT INTO pipeline_state VALUES ('watermark', ?) "
                            "ON CONFLICT(name) DO UPDATE SET value = excluded.value", (newest,))
        write_json_atomic(checkpoint_path, {"run_id": run_id, "since": since, "next_page": None, "done": True})
        log.info("run=%s status=ok %s seconds=%.2f", run_id,
                 " ".join(f"{k}={v}" for k, v in stats.items()), time.perf_counter() - started)
        return stats
    except Exception:
        log.exception("run=%s status=failed %s", run_id, " ".join(f"{k}={v}" for k, v in stats.items()))
        raise
    finally:
        con.close()
```

A few decisions are worth pointing out, because each one answers a question from earlier in the chapter:

- **The watermark is `MAX(updated_at)` from the orders table**, read at the very end. It comes from data that is actually stored (section 8.5), and it is written in the last step, after the data and the Parquet partitions.
- **`last_run` records which run last wrote each row.** At the end, the days to republish are the days of rows this run wrote. Because `last_run` is in the database, a resumed run (same `run_id`, from the checkpoint) also republishes days written **before** the crash.
- **Partitions are rebuilt from SQLite**, never from the page of changes (section 14.4's rule), so each day's partition is complete.
- **The email never leaves the transform**: only `customer_key` reaches SQLite and Parquet. The quarantine file does keep the whole raw record (it is needed for replay), so it lives in the private `state` folder.
- **A resume keeps the same `since`** (it is in the checkpoint), so the resumed run asks the API exactly the same question as the run that crashed.
- **The bad-record threshold is checked before publishing.** Good records were already upserted page by page (that is what makes resume possible); if the threshold fires, the Parquet files and the watermark are not touched, the run fails loudly, and the next run re-fetches the same window.

### 17.3 Running it

The run below uses the fake API from section 2.7, plus one broken order (108, with amount `"N/A"`). Logging goes to the screen; `FakeSleep` and `rand=lambda: 1.0` make any retries instant and repeatable; run ids are fixed (`new_run_id=...`) so the output is the same every time.

```python
import copy
import logging
import os
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pipeline

class ShortTracebacks(logging.Formatter):
    """Only to keep this chapter short: print a traceback as its last line. Do not use in real pipelines."""
    def formatException(self, exc_info):
        return f"Traceback (shortened): {exc_info[0].__name__}: {exc_info[1]}"

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ShortTracebacks("%(levelname)-7s %(name)s: %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
os.environ["PAGEBOUND_PSEUDO_KEY"] = "chapter-demo-key-not-a-real-secret"    # normally set outside Python
cfg = pipeline.load_config(Path("data"))
print(cfg)

server = copy.deepcopy(ORDERS)
server.append({**copy.deepcopy(ORDERS[0]), "id": 108, "amount": "N/A",
               "created_at": "2024-06-04T09:30:00Z", "updated_at": "2024-06-04T09:30:00Z"})
log = []
client = make_client(server, log=log)
stats = pipeline.run(client, cfg, sleep=FakeSleep(), rand=lambda: 1.0, new_run_id="run-A")
```
```text
Config(db_path=PosixPath('data/orders.db'), parquet_root=PosixPath('data/parquet'), state_dir=PosixPath('data/state'), per_page=3, max_pages=1000, overlap=datetime.timedelta(seconds=600), max_attempts=4, max_bad_fraction=0.05, min_records_for_fraction=20)
INFO    pipeline: run run-A: starting, updated_since=None
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=1&per_page=3 "HTTP/1.1 200 OK"
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=2&per_page=3 "HTTP/1.1 200 OK"
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=3&per_page=3 "HTTP/1.1 200 OK"
WARNING pipeline: order 108 quarantined: amount: not a number
INFO    pipeline: run=run-A status=ok pages=3 fetched=8 written=7 quarantined=1 days=4 seconds=0.07
```

(The `seconds` value is a timing from this machine. On Windows the paths print as `WindowsPath(...)`.) Notice that `print(cfg)` shows the paths and settings but **not** the key. The `httpx: HTTP Request: ...` lines come from httpx's own logger, at INFO level: one line per request, with the full URL. That is handy here, and it is exactly why a token must never be put in a URL (section 12.6). Now look at what the run left behind:

```python
import sqlite3

def show_outputs():
    con = sqlite3.connect(cfg.db_path)
    print("orders:", con.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
          "| watermark:", con.execute("SELECT value FROM pipeline_state").fetchone()[0])
    print("emails stored in SQLite:",
          con.execute("SELECT COUNT(*) FROM orders WHERE customer_key LIKE '%@%'").fetchone()[0])
    con.close()
    for path in sorted(cfg.parquet_root.rglob("*.parquet")):
        print("   ", path.relative_to("data").as_posix(), pq.read_metadata(path).num_rows, "rows")

show_outputs()
print(pq.read_table(cfg.parquet_root).sort_by("id").slice(0, 2).to_pylist())
for line in (cfg.state_dir / "quarantine.jsonl").read_text(encoding="utf-8").splitlines():
    entry = json.loads(line)
    print("quarantine:", entry["run_id"], entry["id"], entry["reasons"])
```
```text
orders: 7 | watermark: 2024-06-04T09:00:00+00:00
emails stored in SQLite: 0
    parquet/order_date=2024-06-01/part-0.parquet 2 rows
    parquet/order_date=2024-06-02/part-0.parquet 2 rows
    parquet/order_date=2024-06-03/part-0.parquet 2 rows
    parquet/order_date=2024-06-04/part-0.parquet 1 rows
[{'id': 101, 'customer_key': '3779cf239a17eda0', 'city': 'Pune', 'status': 'shipped', 'amount': Decimal('19.99'), 'created_at': datetime.datetime(2024, 6, 1, 10, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'updated_at': datetime.datetime(2024, 6, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'qty_total': 2, 'order_date': '2024-06-01'}, {'id': 102, 'customer_key': 'fb4cc7bab5a1e11d', 'city': None, 'status': 'pending', 'amount': Decimal('5.50'), 'created_at': datetime.datetime(2024, 6, 1, 11, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'updated_at': datetime.datetime(2024, 6, 1, 12, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC')), 'qty_total': 1, 'order_date': '2024-06-01'}]
quarantine: run-A 108 ['amount: not a number']
```

Seven good orders in SQLite and in four daily Parquet partitions, the bad order in quarantine with its reason, and the watermark at the newest **stored** change (order 107 at 09:00; the quarantined 108 does not count, because it is not stored).

### 17.4 Run it again: nothing changes

```python
log.clear()
stats = pipeline.run(client, cfg, sleep=FakeSleep(), rand=lambda: 1.0, new_run_id="run-B")
print("request:", log)
show_outputs()
```
```text
INFO    pipeline: run run-B: starting, updated_since=2024-06-04T08:50:00Z
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=1&per_page=3&updated_since=2024-06-04T08%3A50%3A00Z "HTTP/1.1 200 OK"
WARNING pipeline: order 108 quarantined: amount: not a number
INFO    pipeline: run=run-B status=ok pages=1 fetched=2 written=0 quarantined=1 days=0 seconds=0.00
request: [{'page': '1', 'per_page': '3', 'updated_since': '2024-06-04T08:50:00Z'}]
orders: 7 | watermark: 2024-06-04T09:00:00+00:00
emails stored in SQLite: 0
    parquet/order_date=2024-06-01/part-0.parquet 2 rows
    parquet/order_date=2024-06-02/part-0.parquet 2 rows
    parquet/order_date=2024-06-03/part-0.parquet 2 rows
    parquet/order_date=2024-06-04/part-0.parquet 1 rows
```

The second run asked for changes since 08:50 (the watermark minus the 10-minute overlap), received order 107 again and the still-broken 108, wrote **nothing**, published no partitions, and left every output exactly as it was. (108 was quarantined a second time; it will be, on every run, until the source fixes it or someone replays it. That repetition is noise, but harmless noise, and it keeps the problem visible.)

### 17.5 A crash, and a resume

Now the source changes: order 105 is cancelled, and two new orders arrive. And this time the network dies after the first page, for longer than the retries can cover:

```python
server[4].update(status="cancelled", updated_at="2024-06-05T08:00:00Z")
for new_id, ts in [(109, "2024-06-05T07:00:00Z"), (110, "2024-06-05T07:30:00Z")]:
    server.append({**copy.deepcopy(ORDERS[1]), "id": new_id, "created_at": ts, "updated_at": ts})

def flaky_client(fail_from_call=None):
    inner = make_handler(server)
    def handler(request):
        log.append(dict(request.url.params))                 # every attempt, including failed ones
        if fail_from_call is not None and len(log) >= fail_from_call:
            raise httpx.ConnectError("network down (simulated)", request=request)
        return inner(request)
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.pagebound.test")

log.clear()
try:
    pipeline.run(flaky_client(fail_from_call=2), cfg, sleep=FakeSleep(), rand=lambda: 1.0, new_run_id="run-C")
except httpx.ConnectError:
    print("run C failed; pages requested:", [entry["page"] for entry in log])
print("checkpoint:", (cfg.state_dir / "checkpoint.json").read_text(encoding="utf-8"))
```
```text
INFO    pipeline: run run-C: starting, updated_since=2024-06-04T08:50:00Z
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=1&per_page=3&updated_since=2024-06-04T08%3A50%3A00Z "HTTP/1.1 200 OK"
WARNING pipeline: order 108 quarantined: amount: not a number
WARNING pipeline: page 2 attempt 1 failed (ConnectError); retrying in 0.50s
WARNING pipeline: page 2 attempt 2 failed (ConnectError); retrying in 1.00s
WARNING pipeline: page 2 attempt 3 failed (ConnectError); retrying in 2.00s
ERROR   pipeline: run=run-C status=failed pages=1 fetched=3 written=1 quarantined=1 days=0
Traceback (shortened): ConnectError: network down (simulated)
run C failed; pages requested: ['1', '2', '2', '2', '2']
checkpoint: {"done": false, "next_page": 2, "run_id": "run-C", "since": "2024-06-04T08:50:00Z"}
```

The first page (orders 107, 108 and 109 in `updated_at` order) was fetched and saved; the second page failed four times (one try plus three retries, with delays of 0.5, 1.0 and 2.0 "seconds" that did not really pass), and the run failed with a summary line marked `status=failed` and a full traceback in the log (shortened to one line here by the `ShortTracebacks` formatter). The checkpoint says: run C, page 2 next, not done. The Parquet files and the watermark were not touched. Now the network is back:

```python
log.clear()
stats = pipeline.run(flaky_client(), cfg, sleep=FakeSleep(), rand=lambda: 1.0, new_run_id="run-D")
print("requests made by the resume:", log)
show_outputs()
con = sqlite3.connect(cfg.db_path)
print(con.execute("SELECT id, status, order_date, last_run FROM orders WHERE last_run <> 'run-A' ORDER BY id").fetchall())
con.close()
```
```text
INFO    pipeline: run run-C: resuming at page 2
INFO    httpx: HTTP Request: GET https://api.pagebound.test/v1/orders?page=2&per_page=3&updated_since=2024-06-04T08%3A50%3A00Z "HTTP/1.1 200 OK"
INFO    pipeline: run=run-C status=ok pages=1 fetched=2 written=2 quarantined=0 days=2 seconds=0.00
requests made by the resume: [{'page': '2', 'per_page': '3', 'updated_since': '2024-06-04T08:50:00Z'}]
orders: 9 | watermark: 2024-06-05T08:00:00+00:00
emails stored in SQLite: 0
    parquet/order_date=2024-06-01/part-0.parquet 2 rows
    parquet/order_date=2024-06-02/part-0.parquet 2 rows
    parquet/order_date=2024-06-03/part-0.parquet 2 rows
    parquet/order_date=2024-06-04/part-0.parquet 1 rows
    parquet/order_date=2024-06-05/part-0.parquet 2 rows
[(105, 'cancelled', '2024-06-03', 'run-C'), (109, 'pending', '2024-06-05', 'run-C'), (110, 'pending', '2024-06-05', 'run-C')]
```

The new run did not start fresh as "run-D": it found an unfinished checkpoint and **resumed run C** at page 2, with the same `updated_since`, making one request. Order 105 is cancelled, 109 (saved before the crash) and 110 (saved by the resume) are both there: nine rows in total (101 to 107, 109 and 110; 108 is still in quarantine), with no duplicates. The days touched by run C, `2024-06-03` (order 105) and `2024-06-05` (109 and 110), were republished; the new `order_date=2024-06-05` partition appeared, and the other days were left alone. Only then did the watermark move to the newest stored change.

### 17.6 Where this pipeline is still simple

This pipeline is complete enough to trust with a small, real job, but you should know what it does not do:

- It uses a **page-number** API. If records change during a run, rows can shift between pages (section 3.8). The overlap and re-runs repair most of that; a cursor API would avoid it.
- **Deletes** at the source are not seen (section 8.7).
- The quarantine file grows with repeats of the same bad record; a real system dedupes it, or keeps a quarantine **table** keyed by `(id, updated_at)`.
- Runs are not protected against running **twice at the same time**. Two simultaneous runs could both resume the same checkpoint. Real schedulers prevent overlap, or the pipeline takes a lock (for example, by creating a lock file with `open(path, "x")`, which fails if the file already exists).
- `delete_matching` is not atomic per partition (section 14.4).

Each of these is a reasonable next step, and the module project leaves room for some of them.

## 18. Testing pipelines

### 18.1 What to test

Pipelines are tested at three levels, and you have seen all the tools already:

1. **Pure functions** (`validate`, `transform`, `pseudonymise`, `mask_email`, backoff delays): plain inputs, plain outputs, many cases. These tests are fast and find most bugs.
2. **One stage against a fake**: a pagination loop against a `MockTransport` handler; an upsert against an in-memory SQLite database; a Parquet writer against `tmp_path`.
3. **The whole run**, end to end, against a fake API and a temporary folder: the properties that matter most, in the form of scenarios.

The end-to-end scenarios are what make a pipeline trustworthy, because they test the promises from section 1.4 directly:

| Promise | Test scenario |
|---|---|
| re-runnable | run twice with the same data; every output is identical |
| resumable | inject a crash on request N; run again; final state equals a clean run; count the resume's requests |
| quarantine, not crash | include bad records; the run succeeds; they are in quarantine with reasons; good records are loaded |
| threshold | make most records bad; the run fails; the watermark did not move |
| safe | no email appears in the database, the Parquet files, or the log (`caplog`) |
| retries | a 429 then 200: the run succeeds, the fake `sleep` recorded the `Retry-After` value |

### 18.2 The building blocks

- **`httpx.MockTransport`** for the API. The handler records each request's parameters, so a test can assert **how many** requests were made and **which** parameters were sent. A handler can also raise `httpx.ConnectError` on a chosen call (crash injection), return 429 or 503 (retry paths), or always say "next page" (an endless API, to test the `max_pages` guard).
- **`tmp_path`**, pytest's fixture that gives each test its own empty folder, for the database, Parquet files, checkpoint and quarantine. Tests never touch your real data and never interfere with each other.
- **Fake time**: pass `sleep=FakeSleep()` and `rand=lambda: 1.0` so retries take no time and delays are exact; pass `now=lambda: fixed_datetime` for anything that reads the clock.
- **`monkeypatch.setenv` / `monkeypatch.delenv`** (or an `env` argument) for secrets.
- **`caplog`**, pytest's fixture that captures log records, to assert what was (and was not) logged.

### 18.3 A test file for the pipeline

Here is a test file for `pipeline.py` from section 17. It builds its own small data set, so it does not depend on anything else in the chapter. Read each test as a sentence: the name says the promise, and every `assert` message says what the likely bug is when it fails.

```python
import copy
import json
import sqlite3

import httpx
import pyarrow.parquet as pq
import pytest

import pipeline

def order(id, updated_at, amount="10.00", email=None):
    return {"id": id, "customer": {"email": email or f"user{id}@example.com", "city": "Pune"},
            "status": "shipped", "amount": amount, "currency": "INR",
            "created_at": updated_at, "updated_at": updated_at, "items": [{"sku": "B1", "qty": 1}]}

ORDERS = [order(1, "2024-06-01T10:00:00Z"), order(2, "2024-06-01T11:00:00Z"),
          order(3, "2024-06-02T09:00:00Z"), order(4, "2024-06-02T10:00:00Z"),
          order(5, "2024-06-03T08:00:00Z")]

class FakeAPI:
    """Page-number API over a list of orders. Records every request; can fail or rate-limit."""

    def __init__(self, orders, fail_from_call=None, rate_limit_first=False):
        self.orders, self.fail_from_call, self.rate_limit_first = orders, fail_from_call, rate_limit_first
        self.requests = []

    def __call__(self, request):
        self.requests.append(dict(request.url.params))
        if self.fail_from_call is not None and len(self.requests) >= self.fail_from_call:
            raise httpx.ConnectError("simulated outage", request=request)
        if self.rate_limit_first and len(self.requests) == 1:
            return httpx.Response(429, headers={"Retry-After": "3"})
        p = request.url.params
        rows = sorted(self.orders, key=lambda o: (o["updated_at"], o["id"]))
        if "updated_since" in p:
            rows = [o for o in rows if o["updated_at"] > p["updated_since"]]
        page, size = int(p["page"]), int(p["per_page"])
        chunk = rows[(page - 1) * size: page * size]
        return httpx.Response(200, json={"data": chunk, "page": page,
                                         "next_page": page + 1 if page * size < len(rows) else None})

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self), base_url="https://api.pagebound.test")

class FakeSleep:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)

@pytest.fixture
def cfg(tmp_path, monkeypatch):
    monkeypatch.setenv("PAGEBOUND_PSEUDO_KEY", "test-key")
    return pipeline.load_config(tmp_path)

def run(api, cfg, run_id="r1", sleep=None):
    return pipeline.run(api.client(), cfg, sleep=sleep or FakeSleep(), rand=lambda: 1.0, new_run_id=run_id)

def snapshot(cfg):
    con = sqlite3.connect(cfg.db_path)
    rows = con.execute("SELECT id, customer_key, status, amount_cents, updated_at FROM orders ORDER BY id").fetchall()
    con.close()
    parquet = sorted(pq.read_table(cfg.parquet_root).column("id").to_pylist())
    return rows, parquet

def test_running_twice_gives_the_same_result(cfg):
    api = FakeAPI(copy.deepcopy(ORDERS))
    run(api, cfg, "r1")
    first = snapshot(cfg)
    stats = run(api, cfg, "r2")
    assert stats["written"] == 0, "a re-run with no new data wrote rows: is the upsert 'only if newer'?"
    assert snapshot(cfg) == first, "a re-run changed SQLite or Parquet: some write is not idempotent"
    assert first[1] == [1, 2, 3, 4, 5], "Parquet should hold each order exactly once"

def test_resume_after_crash_loads_everything_once(cfg):
    crashing = FakeAPI(copy.deepcopy(ORDERS), fail_from_call=2)
    with pytest.raises(httpx.ConnectError):
        run(crashing, cfg, "r1")
    healthy = FakeAPI(copy.deepcopy(ORDERS))
    run(healthy, cfg, "r2")
    assert [r["page"] for r in healthy.requests] == ["2"], (
        "the resumed run should continue at page 2 only; did it ignore the checkpoint?")
    rows, parquet = snapshot(cfg)
    assert [r[0] for r in rows] == [1, 2, 3, 4, 5], "after resume every order must be in SQLite once"
    assert parquet == [1, 2, 3, 4, 5], "days written before the crash must be published by the resume too"

def test_bad_records_are_quarantined_not_fatal(cfg):
    data = copy.deepcopy(ORDERS) + [order(6, "2024-06-03T09:00:00Z", amount="N/A")]
    stats = run(FakeAPI(data), cfg)
    assert stats["quarantined"] == 1, "exactly one record (amount 'N/A') should be quarantined"
    lines = (cfg.state_dir / "quarantine.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])["id"] == 6 and json.loads(lines[0])["reasons"], "quarantine needs id and reasons"
    assert [r[0] for r in snapshot(cfg)[0]] == [1, 2, 3, 4, 5], "the good records must still be loaded"

def test_too_many_bad_records_fails_and_keeps_watermark(cfg):
    data = [order(i, f"2024-06-01T1{i}:00:00Z", amount="N/A") for i in range(1, 4)] + [order(9, "2024-06-01T09:00:00Z")]
    with pytest.raises(pipeline.TooManyBadRecords):
        run(FakeAPI(data), cfg)
    con = sqlite3.connect(cfg.db_path)
    assert con.execute("SELECT COUNT(*) FROM pipeline_state").fetchone()[0] == 0, (
        "the watermark must not move when the run aborts")
    con.close()

def test_no_email_in_outputs_or_logs(cfg, caplog):
    caplog.set_level("INFO", logger="pipeline")
    data = copy.deepcopy(ORDERS) + [order(7, "2024-06-03T09:00:00Z", amount="-1.00", email="secret@example.com")]
    run(FakeAPI(data), cfg)
    rows, _ = snapshot(cfg)
    assert not any("@" in str(value) for row in rows for value in row), "an email reached SQLite"
    table = pq.read_table(cfg.parquet_root)
    assert not any("@" in str(v) for col in table.columns for v in col.to_pylist()), "an email reached Parquet"
    assert "@" not in caplog.text, "an email was logged; log ids, not records"

def test_429_is_retried_with_retry_after(cfg):
    sleep = FakeSleep()
    stats = run(FakeAPI(copy.deepcopy(ORDERS), rate_limit_first=True), cfg, sleep=sleep)
    assert sleep.delays == [3.0], "after a 429 with Retry-After: 3 the pipeline should wait exactly 3 s, once"
    assert stats["fetched"] == 5, "after the retry, every order should be fetched"
```

Running it:

```bash
pytest -q test_pipeline.py
```

```text
......                                                                   [100%]
6 passed in 0.49s
```

(The time at the end is from this machine.) Six tests, each a few milliseconds, no network, no real sleeping, and no files outside the test's own temporary folder. Because the tests are fast, you can run them after every change, and a change that breaks idempotency or resume is caught at once instead of at 3 a.m.

### 18.4 Make the tests fail first

A test that has never failed might not test anything. When you write a test for a promise like "resume continues at page 2", break the code on purpose once (for example, swap the "data first, checkpoint second" lines, or remove the `WHERE` from the upsert) and check that the right test fails, with a message that points at the bug. The problems in this module are built the same way: each `starter.py` fails the tests, and the assert messages name the likely mistake.

### 18.5 Hand-trace step-by-step tests

Tests that walk through steps (pages, runs, crash points, watermarks) are the easiest to get wrong, because the expected values come from a mental model, and the model can be wrong. Before trusting such a test, **trace it by hand** on paper: write down, for each request, the parameters sent, the records returned, what is saved, and what the checkpoint and watermark hold afterwards. The `resume` test above was traced like this:

```text
run r1 (fails from call 2):  call 1 page=1 -> orders 1,2,3 -> upsert 3 rows -> checkpoint next_page=2
                             call 2 page=2 -> ConnectError; retries: calls 3,4,5 also fail -> raise
run r2:  checkpoint not done -> resume run r1 at page 2, same since (None)
                             call 1 page=2 -> orders 4,5 -> upsert 2 rows -> next_page None -> checkpoint done
         publish days with last_run = r1: 2024-06-01, 2024-06-02, 2024-06-03 -> watermark = 2024-06-03T08:00Z
```

If the trace and the test disagree, one of them is wrong, and it is worth finding out which before going on.

## 19. Module project preview

The module project is the pipeline of section 17, built by you, to a written contract, and tested much harder. You will write an **incremental, resumable pipeline from the fake Pagebound Orders API into SQLite and partitioned Parquet**. The test suite will feed it fixture pages (JSON files) through a `MockTransport` and check that it:

- **loads incrementally**: a watermark in SQLite; a second run with no new data writes nothing; changed records update in place, only if newer;
- **is re-run safe**: running twice, or re-running a day, gives the same SQLite table and the same Parquet partitions;
- **resumes**: crashes injected at different points (first page, middle page, last page, after the data but before the checkpoint) all end, after a resume, in the same state as a clean run, with the resume making no more requests than needed;
- **retries** 429 and 5xx with backoff (honouring `Retry-After`), and does **not** retry 4xx;
- **guards against an endless API** with a page limit and a clear error;
- **quarantines** bad records with reasons, and fails the run (without moving the watermark) when too many are bad;
- **pseudonymises** customer emails with HMAC and a key from an environment variable (with a clear error if it is missing), so no email appears in SQLite, Parquet or the logs;
- **logs** a one-line run summary with counts.

How to approach it:

1. **Read the contract** in the problem statement twice: page format, `>` or `>=`, the required schema, the thresholds.
2. **Build the pure parts first** (`validate`, `transform`, `pseudonymise`) and test them alone.
3. **Then extract with retries**, against a tiny handler.
4. **Then the load** (upsert, Parquet partitions), then **state** (checkpoint, watermark), and only then `run()`.
5. **Trace the crash scenarios by hand** (section 18.5) before running the big tests.
6. When a test fails, read its message first: it names the promise you broke.

Most problems in this module practise one piece of the project in isolation (pagination, retries, checkpoints, upserts, partitions, pseudonymisation), so by the time you reach it, every piece will be familiar.

## 20. Summary

- A **pipeline** copies data from a source to a sink: **extract, transform, load**. Good means **correct, re-runnable, resumable, observable** and **safe**. "Run twice = same result" (idempotency) is the property everything else leans on.
- **httpx**: use one `Client` with a `base_url` and a **timeout**; call `raise_for_status()` before `.json()` (httpx does not raise for 4xx/5xx on its own); handle non-JSON bodies with a clear error (`raise ... from exc`) and 204 No Content. `httpx.MockTransport` runs everything offline and is how pipelines are tested.
- **Pagination**: page number, offset/limit, cursor, Link header (`response.links`). Let the **server** say when to stop; never stop on a short page unless the contract promises full pages; always have a **`max_pages`** guard that **raises**. Offset pagination skips and duplicates rows when data changes; cursors (keyset) do not.
- **ETL** transforms in Python before loading; **ELT** loads raw JSON first and transforms with SQL (`json_extract`, `json_valid`, `json_array_length`). Keeping a **raw layer** lets you replay fixes without re-fetching.
- **Transform**: flatten nested objects into prefixed columns and nested lists into a child table or summaries; money as **`Decimal`** from strings (not floats; `InvalidOperation` is not a `ValueError`; check `is_finite()`), stored as integer cents; timestamps parsed to **aware UTC** datetimes; one written-down rule for which time zone defines a "day"; normalise strings and turn `""` into `None`. Keep transforms **pure**.
- **Checks**: a schema (contract) per record (watch `bool` being an `int`), data-quality rules per record and per batch (nulls, uniqueness, ranges, referential, freshness, volume), each with a decided action: quarantine, warn or fail.
- **Bad records** go to a **quarantine** (JSONL with reasons and run id), never silently dropped, never crashing the run. Catch the **data** exceptions you expect, per record. A **failure threshold** stops the run when bad records are no longer occasional.
- **Incremental loads** use a **watermark** taken from the data (not the clock), moved only after the data is committed. Prefer **`>=`** and an **overlap window**: re-fetching is harmless with an idempotent sink; missing data is silent and permanent. Incremental loads cannot see deletes.
- **Idempotent writes**: a natural key; **UPSERT only if newer** (`WHERE excluded.updated_at > table.updated_at`); not `INSERT OR REPLACE`; **delete + insert per partition in one transaction** for computed outputs and backfills. At-least-once delivery plus an idempotent sink gives "effectively once".
- **Retries**: retry transport errors, 429 and 5xx; never other 4xx. Exponential backoff capped at `max_delay` with **equal jitter** (`backoff/2 + rand() * backoff/2`; full jitter is the alternative), honour **`Retry-After`** exactly but capped, a maximum number of attempts, retries at one level only. Inject `sleep` and `rand` so tests are instant and exact.
- **Checkpoints**: save the minimum state to continue (cursor or page, run id, `since`); write files **atomically** (temp file in the same folder, `fsync`, `os.replace`); **data first, checkpoint second**, or both in one database transaction. A crash may repeat a page; it must never skip one.
- **Logging**: configure once; a **run id** on everything; one **summary line** with counts and duration; WARNING for retries and quarantines; `log.exception` then re-raise on failure. **Never log** secrets, tokens, headers or personal data.
- **CSV** forgets types and nulls; **Parquet** is columnar, compressed and typed. Declare an explicit **pyarrow schema** (`int64`, `string`, `decimal128`, `timestamp(tz="UTC")`); `pq.write_table` / `pq.read_table`; read only the columns you need.
- **Partitioning**: Hive-style `key=value` folders by a stable, moderately varied column (usually a date); `write_to_dataset` with `basename_template` and **`existing_data_behavior="delete_matching"`** to **replace** partitions; always write the **complete** partition; avoid the small-files problem.
- **Schema evolution**: be tolerant in reading and strict in writing; add columns with `ALTER TABLE ... ADD COLUMN` idempotently; read old and new Parquet with a **unified** schema (or one declared schema), since by default extra columns can be silently dropped; type changes and renames need a migration.
- **Sensitive data**: an **allow-list** of columns; **mask** for display; **pseudonymise with HMAC-SHA256** and a secret key from the environment (plain hashes fall to dictionary attacks; pseudonymised data is still personal data); secrets never in code, git, URLs or logs; **least privilege** with per-role views and file permissions; a **retention** period for every dataset, including raw data, quarantine and logs.

Next come the problems for this module. They practise each section on its own, and they end with the module project, which puts the whole chapter to work.
