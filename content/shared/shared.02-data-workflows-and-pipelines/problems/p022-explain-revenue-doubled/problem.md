# Explain: "we re-ran the job and revenue doubled"

You are on call for the Pagebound data team. This message arrives on Monday morning:

> The nightly `daily_orders` job failed on Sunday at 02:10 with a timeout from the Orders API.
> The scheduler retried it automatically at 02:20 and it succeeded. Later, to be safe, Ravi ran
> it once more by hand for Sunday. Now the dashboard says Sunday's revenue was **₹3.1 lakh**; the
> payment provider says ₹1.2 lakh. Saturday looks right. What happened, and how do we make sure
> it never happens again? Ravi says "let's just make sure the job only ever runs once".

The job (simplified):

```python
def daily_orders(client, conn, day):
    page = 1
    while page is not None:
        body = call_with_retry(client, "/v1/orders", {"created_on": day, "page": page})
        for o in body["data"]:
            conn.execute(
                "INSERT INTO orders (id, day, amount) VALUES (?, ?, ?)",   # no key on id
                (o["id"], day, o["amount"]),
            )
        conn.commit()                 # after every page
        page = body["next_page"]
```

```sql
-- the dashboard
SELECT day, SUM(amount) AS revenue FROM orders GROUP BY day;
```

Write `answer.md` (about 250 to 450 words) with these parts:

1. **What happened.** Explain, step by step through the three runs, why Sunday's revenue is
   about 2.6 times too high and not exactly 2 or 3 times, and why Saturday is fine.
2. **Why "only run once" is not the fix.** Use the words *at-least-once* and *exactly-once*:
   what can a pipeline realistically guarantee about how many times a page is processed, and
   why? Name at least two ordinary events (other than a human re-run) that cause a repeat.
3. **The fix.** Define *idempotent* in one sentence. Propose a concrete change to the code or
   the table so that running the job for the same day any number of times gives the same
   table. Give the key SQL. Mention one more place that must change: the retry inside a run, or
   the order of commit and checkpoint.
4. **Clean-up and proof.** How do you repair Sunday's data now (one SQL idea), and what
   automated test would have caught this before it shipped?

**Example of the level of detail expected (a different incident)**

> *"The weekly email went out twice."* The sender retries when the mail API times out, but the
> first attempt had actually been delivered; the timeout happened while waiting for the reply.
> A timeout does not mean "it did not happen". Fix: send with an idempotency key (the week's
> id), so the mail API drops a second request with the same key.
