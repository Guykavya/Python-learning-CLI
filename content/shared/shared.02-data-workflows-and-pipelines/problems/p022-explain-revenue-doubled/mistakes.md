- Saying "the data was loaded three times" and expecting 3x. Run 1 committed only part of the
  day before it failed; that is why the factor is about 2.6.
- Blaming the dashboard query. `SUM` is correct; the table contains duplicates.
- Accepting "make it run only once" as the fix. Retries, resumes and backfills are features you
  want; removing them trades duplicates for lost data.
- Defining idempotent as "the job does not fail" or "the job runs once". It means repeating it
  gives the same result.
- Proposing `INSERT OR IGNORE`. It stops duplicates but freezes the first version of every order,
  so a refund or a corrected amount never arrives.
- Proposing `DELETE FROM orders WHERE day = ?` at the start of the run, outside a transaction,
  with commits per page. A crash in the middle then leaves the day half empty: under-reporting
  instead of over-reporting.
- Proposing `SELECT DISTINCT` in the dashboard. It hides the symptom in one query and breaks
  legitimate equal rows; every other consumer still sees duplicates.
- No test. Without a "run it twice" test, the next refactor brings the bug back.
