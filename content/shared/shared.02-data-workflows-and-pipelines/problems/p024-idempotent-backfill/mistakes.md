- Deleting the day first and then fetching (or inserting page by page with commits). A network
  error on page 2 leaves the day half empty, and the dashboard under-reports until someone
  notices.
- `DELETE`, `commit()`, then `INSERT`. Two transactions: a rejected row leaves the day empty.
- Only upserting, without the `DELETE`. Re-runs are idempotent, but orders deleted at the source
  stay forever (orders 40 and 90).
- Deleting the whole range up front (`DELETE ... WHERE order_date BETWEEN ? AND ?`). A crash on
  day 3 of 30 wipes 27 days that were fine.
- Plain `INSERT`. Order 5 appears on two pages and order 7 is already stored under another day:
  both raise `IntegrityError`. `INSERT OR IGNORE` hides the error but keeps order 7 under the wrong
  day.
- Counting `len(all items)` instead of distinct ids: order 5 is counted twice.
- `while day < end`: the end day is part of the range.
- Building date strings by hand (`f"2024-06-{d:02d}"`): it breaks at the end of every month and on
  leap days. `date + timedelta(days=1)` knows the calendar.
- Converting values (`str(o["amount"])`). `None` becomes the string `"None"`, the `NOT NULL` check
  never fires, and a broken record is loaded as if it were fine.
