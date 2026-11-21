## Approach

| # | What happens | Client gets |
|---|---|---|
| 1 | connection **refused** at once (machine up, nothing listens); no other backend | **502** |
| 2 | nobody answers on the stale address; the connect attempt **times out** | **504** |
| 3 | the backend accepted but the answer takes 8 s; `proxy_read_timeout` is 5 s | **504** (after 5 s) |
| 4 | the answer is not valid HTTP | **502** |
| 5 | everything works | **200** |
| 6 | the first attempt is refused, Nginx retries the `GET` on the healthy backend | **200** (the client never sees the failed attempt) |

Reading the log: `"status":502, "upstream_status":"-"` means no backend ever answered; `"504, 504, 504"` means three backends were tried and all timed out (the slow request ran three times, which is why slow or costly endpoints should set `proxy_next_upstream off;`, chapter 7.4).

## Cost

Reading only. The answers come from the chapter's captured experiments (stopped backend gave 504 with a stale address; the 8-second request gave 504 after retries), not from memory about Nginx.

## Another way

Reproduce situations 1 to 3 on your machine with the chapter's Compose stack (`docker compose stop api`, `curl -s -o /dev/null -w '%{http_code}' localhost:18080/`, `/slow?seconds=8`) and compare. The exact timing and addresses will differ, but the status codes follow the same rules.
