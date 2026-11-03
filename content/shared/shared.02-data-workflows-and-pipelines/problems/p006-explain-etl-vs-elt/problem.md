# Explain: ETL or ELT?

**ETL** (extract, transform, load) cleans the data *before* it reaches the destination; only
the finished rows are stored. **ELT** (extract, load, transform) stores the data as it came
(the **raw** layer) and transforms it later, inside the destination, usually with SQL, into
**staging** and **clean** tables.

Pagebound has two jobs to build. Both read the same Pagebound Orders API, whose orders look like this:

```json
{"id": 101, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
 "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
 "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]}
```

**Scenario 1: the analytics database.** Every night, the orders of the day (about 20,000) go
into a SQLite database that two analysts query. The analysts are still arguing about what
"revenue" means (with or without cancelled orders? before or after refunds? converted to one
currency?) and change their minds every few weeks. When they do, they want last year's numbers
recalculated with the new rule. The API only lets you read orders from the last 90 days.

**Scenario 2: the courier export.** Every morning, a CSV file goes to a courier company's
upload server. The courier needs exactly four columns in a fixed order: `order_id`, `city`,
`item_count`, `ship_by_date`, and only for orders with status `shipped`. The contract with the
courier says they must **never** receive customer emails or amounts. Their system just reads
the CSV; it cannot run SQL or any transformation.

Write `answer.md` (about 200 to 450 words). For **each** scenario:

1. Choose ETL or ELT.
2. Give **two concrete reasons** that come from the scenario (not general facts about ETL/ELT).
3. Say what is stored where: which layers exist (raw / staging / clean, or only the final
   output) and what one row of each looks like.
4. Name **one risk or cost** of your choice and one way to reduce it.

**Example of the level of detail expected (a different scenario)**

> *A weekly job copies product prices from a supplier's API into the shop database, where they
> are shown on the website.* ETL. The website must never show a half-cleaned price (a string
> like `"19,99 EUR"`), so only validated rows may reach the shop table; and nobody needs the
> supplier's raw format later, because the supplier's API can be read again at any time. Stored:
> only `products(sku, price_cents, updated_at)`. Risk: a parsing rule that is wrong throws data
> away for good; reduce it by writing the rejected rows to a quarantine file so they can be
> re-processed after the fix.
