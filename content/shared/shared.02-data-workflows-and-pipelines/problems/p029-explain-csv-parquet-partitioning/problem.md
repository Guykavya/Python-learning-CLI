# Explain: CSV or Parquet, and how to partition

The Pagebound pipeline now has three new consumers. For each one, the team asks you: which file
format, and should the data be partitioned, and by what?

**Scenario A: the auditor.** Once a month the finance team must send the auditor all orders of
that month: about 2,000 rows, 9 columns. The auditor opens it in Excel and has no Python.

**Scenario B: the analysts.** Three years of orders: 50 million rows, 30 columns. Almost every
dashboard query looks at the **last 7 or 30 days** and reads 3 or 4 columns (`amount`, `status`,
`city`, `created_at`). Today it is one 9 GB CSV file and every query takes minutes. A colleague
suggests partitioning it by `customer_id` "because we have many customers".

**Scenario C: the warehouse sensor log.** A warehouse temperature sensor sends about 200 readings
per day. The data goes back 5 years. Someone proposes Parquet partitioned by
`date=YYYY-MM-DD/hour=HH` "so it looks just like the big datasets".

Write `answer.md` (about 250 to 450 words) with, for **each** scenario:

1. The format (CSV or Parquet) and the partitioning (none, or the key and its granularity).
2. **Two concrete reasons** tied to the scenario's numbers or users (who reads it, how much is
   read, what breaks).
3. **One risk or trap** of your choice and how you would avoid it.

For Scenario B also say what is wrong with the colleague's `customer_id` idea, and for Scenario C
what is wrong with the `date/hour` idea.

**Example of the level of detail expected (a different scenario)**

> *A nightly 300-row list of low-stock books for a shop manager who reads it on a phone.*
> CSV, no partitioning. Reasons: it is tiny, so Parquet's compression and column pruning save
> nothing; the manager's phone opens CSV but not Parquet. Risk: a book code like `0071` loses its
> leading zeros in a spreadsheet; quote it or prefix it so it stays text.
