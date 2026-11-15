**1. Problems**

- **Secret in the code.** `API_TOKEN` is in the source file, so everyone who can read the repository
  or its git history (including every old clone and fork) can call the API as us, forever, even after
  the line is deleted. Fix: read it at run time with `os.environ["PAGEBOUND_API_TOKEN"]` (or a
  secret store), fail clearly if it is missing, and **rotate** the leaked token now.
- **The token is logged.** `log.debug("client headers: %s", ...)` writes the `Authorization` header
  to a log file in a shared folder at DEBUG level. Anyone who can read `/srv/shared/logs` gets the
  token. Fix: log at INFO in production, never log headers or config objects, log only "client ready".
- **Full records in the logs.** `log.info("loading order %s", json.dumps(order))` copies every
  email and city into a file that has no access control and is often kept and backed up longer
  than the data itself. Fix: log ids and counts only (`loaded 482 orders, run_id=...`).
- **Raw PII readable by the whole team.** `warehouse.db` with the full JSON bodies sits in a folder
  everyone can read; SQLite has no users, so file access is the only boundary. Fix: keep the raw
  database in a folder only the pipeline's service account can read (`chmod 600`, owner = the job),
  pseudonymise emails with HMAC in the clean tables, and give each role a separate file or view
  with only the columns it needs.
- **The marketing export leaks emails.** Marketing asked for totals per city, but gets every
  customer's email in a shared folder. Collect and share only what the question needs (data
  minimisation).
- **No retention.** `raw_orders` grows forever "just in case". Every extra year is more data to
  leak and to delete when a customer asks. Fix: a retention rule (for example delete raw bodies
  after 90 days, keep only aggregated or pseudonymised data longer) run by the job itself.

**2. The export, rewritten.** One row per city: `city, orders, revenue`, computed in SQL with
`GROUP BY city` and amounts summed as exact decimals. It answers the question completely and
contains no personal data at all, so it can live in the shared folder safely. Cities with very few
orders could be merged into "other" so a single customer cannot be singled out.

**3. Not enough on its own.** Hashing emails with plain `sha256` looks safe, but anyone with a list
of candidate emails can hash them and match the results (a dictionary attack), so the "anonymous"
export is still personal data. Use an HMAC with a secret key kept away from the data, and still
only share it with people who need customer-level data.
