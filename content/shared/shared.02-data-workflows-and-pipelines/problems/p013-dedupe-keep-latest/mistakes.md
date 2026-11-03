- Comparing the `updated_at` strings. It works only while every timestamp uses the same offset
  and the same format; one `+05:30` value silently picks the wrong version.
- Keeping simply the **last** record for each id (`best[r["id"]] = r`). The API can send an older
  version after a newer one (an overlap window, a retried page), and the old one would win.
- Using `>` instead of `>=`. On a tie the first version stays, but the rule says the last seen
  wins.
- Sorting the result by id or by time. The rule is first-seen order; a dict already gives it.
- Building the result with `{r["id"]: r for r in sorted(records, ...)}` and forgetting that the
  sort changed the key order.
- Modifying the records (for example storing the parsed datetime back into `record["updated_at"]`).
  The caller still needs the original strings.
- Using `datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")`: it rejects `+05:30` and produces a **naive**
  datetime, which cannot be compared with an aware one.
