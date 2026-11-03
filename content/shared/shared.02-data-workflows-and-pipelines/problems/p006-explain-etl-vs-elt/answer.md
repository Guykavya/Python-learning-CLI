**Scenario 1: the analytics database. ELT.**

Reasons:

1. The transformation rules keep changing, and old data must be recalculated with each new
   rule. With ELT the original orders are kept in a raw table, so a new definition of revenue is
   just a new SQL query (or a rebuilt clean table) over all the raw rows.
2. The source cannot be re-read: the API only returns the last 90 days. If we transformed first
   and stored only "revenue as defined in June", the details needed for a new rule (status,
   refunds, currency) would be gone for everything older than 90 days. The raw layer is our only
   copy of history.

Layers: `raw_orders(loaded_at, payload)` with one row per order holding the JSON text exactly as
received; `stg_orders(id, email, city, status, amount, currency, created_at, updated_at)` with
typed, flattened columns extracted from the JSON; and clean tables or views such as
`daily_revenue(day, revenue)` built from staging with the rule of the moment.

Risk: the raw layer keeps everything, including customer emails, so it is a larger and more
sensitive store. Reduce it: only the pipeline account may read `raw_orders` (the analysts use
the staging and clean views), and old raw rows can be pseudonymised or deleted after a
retention period.

**Scenario 2: the courier export. ETL.**

Reasons:

1. The destination must never receive emails or amounts. In ELT the raw data would land at the
   courier first and be cleaned there, which breaks the contract the moment it is loaded. The
   sensitive fields must be removed before anything leaves our system.
2. The destination cannot transform anything: it only reads a CSV with four fixed columns. So
   the filtering (`shipped` only), flattening (`city` out of `customer`), counting
   (`item_count`) and the `ship_by_date` calculation must all happen in our code.

Stored at the destination: only the final file, one line per shipped order, for example
`101,Pune,1,2024-06-03`. Nothing raw, no staging. (On our side we may keep our own raw copy for
debugging; it never leaves our system.)

Risk: a bug in the transform (a wrong date rule, a dropped city) goes straight to the courier
and cannot be fixed by re-running SQL on their side. Reduce it by validating the output before
sending it (four columns, no `@` anywhere, no empty city, row count close to yesterday's) and
quarantining rows that fail instead of sending them.
