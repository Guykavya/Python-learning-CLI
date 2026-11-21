# 502 or 504?

Chapter section 7.4 (when the backend is down: 502 and 504). Nginx sits in front of the API. For each situation write the **status code the client receives** (`200`, `502` or `504`). Use the chapter's rules:

| Status | Meaning | Usual cause |
|---|---|---|
| 502 Bad Gateway | Nginx could not get a valid answer from the backend | the app is down or crashed (the machine is up, nothing listens, the connection is **refused at once**), or the answer is malformed |
| 504 Gateway Timeout | the backend accepted, or never answered, within the timeout | a slow request (`proxy_read_timeout`), or an address that nobody answers on (the connection **times out** after `proxy_connect_timeout`: for example a stale address from a container that is gone) |

And two behaviours of the default configuration: Nginx **retries an idempotent request such as `GET` on the next backend** after an error or a timeout, and it answers with the last failure only when every backend failed. Settings of the examples: `proxy_connect_timeout 2s;`, `proxy_read_timeout 5s;`.

1. The API process crashed inside its still-running container. Nginx has one backend; the port refuses connections. A `GET` arrives.
2. A deploy removed the old API container. Nginx still holds its old address (cached for a few seconds); nobody answers on that address. One backend. A `GET` arrives.
3. One backend. The app needs 8 seconds for `GET /slow`.
4. One backend. The app answers with bytes that are not valid HTTP.
5. One backend, healthy, answers in 50 ms.
6. Two backends. One has crashed and refuses connections; the other is healthy. A `GET` arrives, and Nginx happens to try the crashed one first.

## Answer format

Write exactly six lines, one per situation, in this form (number, colon, space, status):

```text
1: 502
2: 504
...
```

## After you answer

- Which log field would have shown the difference between situations 1 and 2 at a glance? (Think of `upstream_status`.)
- In situation 3, what would a `GET` look like in the log if there were **three** backends and the default retry behaviour? (See the chapter's slow-request experiment.)
