# Explain: a privacy review of a pipeline

A colleague wrote the nightly Pagebound job below. It works, the numbers are right, and it is
about to be scheduled on the shared team server. Your lead asks you for a **privacy and
security review** before it goes live.

```python
import json
import logging
import sqlite3

import httpx

logging.basicConfig(filename="/srv/shared/logs/pipeline.log", level=logging.DEBUG)
log = logging.getLogger("pipeline")

API_TOKEN = "pb_live_7f3a9c21e8d64b0f"          # TODO move somewhere else later


def run():
    client = httpx.Client(base_url="https://api.pagebound.test",
                          headers={"Authorization": f"Bearer {API_TOKEN}"})
    log.debug("client headers: %s", client.headers)
    orders = client.get("/v1/orders", params={"page": 1, "per_page": 500}).json()["data"]

    conn = sqlite3.connect("/srv/shared/warehouse.db")      # whole team can read /srv/shared
    conn.execute("CREATE TABLE IF NOT EXISTS raw_orders (id INTEGER PRIMARY KEY, body TEXT)")
    for order in orders:
        log.info("loading order %s", json.dumps(order))
        conn.execute("INSERT OR REPLACE INTO raw_orders VALUES (?, ?)",
                     (order["id"], json.dumps(order)))
    conn.commit()

    with open("/srv/shared/exports/marketing.csv", "w", encoding="utf-8") as f:
        for order in orders:
            f.write(f"{order['customer']['email']},{order['customer']['city']},{order['amount']}\n")
    # raw_orders is never cleaned up: "we might need it one day"
```

The marketing team only wants to know **how many orders and how much revenue per city**.

Write `answer.md` (about 300 to 450 words):

1. **Find at least five distinct problems.** For each one say *what* is wrong, *who* could see or
   misuse the data because of it (be concrete: "everyone with access to /srv/shared", "anyone who
   can read the git history"), and the *fix*. Cover at least: the secret, the logs, the access to
   the database, the marketing export, and retention.
2. **The marketing export, rewritten.** Say in two or three sentences what it should contain
   instead, and why that is enough for marketing's question.
3. **One thing that is not enough on its own.** Pick one common "fix" (for example "we masked the
   emails", "we hashed the emails with sha256", "the folder is hidden") and explain why it does not
   solve the problem by itself.

**Example of the level of detail expected (a different snippet)**

> *`print(f"connecting with password {password}")` in a script run by a cron job.*
> Problem: the password goes to the cron mail and to any log that captures stdout, which many
> people and backup systems can read. Fix: never print secrets; log "connecting as user X" and
> read the password from an environment variable or secret store at run time.
