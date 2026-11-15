# Fix: the pipeline that duplicates and loses orders

A teammate wrote the nightly order loader in `starter.py`. It works on a good night: it pages
through the Pagebound Orders API, writes the orders into SQLite, keeps a checkpoint so it can
resume after a crash, and deletes the checkpoint when it is done. Two incident reports came in.

**Incident 1: "Revenue doubled."** The scheduler ran the job at 02:00, and an engineer ran it
again by hand at 09:00 to "make sure". Every order is now in the table twice and the revenue
report shows twice the real amount.

**Incident 2: "Orders went missing."** One night the API sent order 105 with `"items": null`.
`transform` crashed with a `TypeError`, which is fine: a broken response should stop the run.
The API team fixed the record and the job was started again. It resumed from the checkpoint and
finished without errors, but orders 104, 105 and 106 are not in the table.

**The API** (page pagination):

```
GET /v1/orders?page=<n>&per_page=<k>  ->  {"data": [<order>, ...], "page": n, "next_page": n + 1 or null}
```

Your `solution.py` starts as a copy of this code (`starter.py`). Find the two bugs and fix them. After your fix:

- Running the job any number of times leaves **one row per order id**. If an order changed on
  the server between runs, its row holds the **new** values.
- After a crash while processing page `k`, the next run **resumes at page `k`** (not page 1, not
  page `k + 1`), and at the end every order is in the table exactly once. This must hold
  wherever the crash happens: in the request, in `transform`, or while writing to the database.
- Everything else stays as it is: the function signature, the request parameters, the
  checkpoint format `{"next_page": n}`, deleting the checkpoint after a successful run, the return
  value (orders loaded by this call), the column names, and errors still propagate (a crash
  must still be a crash, do not catch it).

You may change the `CREATE TABLE` statement; the tests always start with a new database file.

**Example** (7 orders 101-107, `per_page=3`, so pages hold 101-103, 104-106 and 107)

```python
run(client, "orders.db", "cp.json")      # 7
run(client, "orders.db", "cp.json")      # 7 again, and the table still has 7 rows (buggy: 14)

# fresh database, the API breaks order 105:
run(client, "orders.db", "cp.json")      # TypeError; cp.json holds {"next_page": 2}  (buggy: 3)
# the API team fixes order 105
run(client, "orders.db", "cp.json")      # 4  (requests pages 2 and 3); table has all 7 orders
```
