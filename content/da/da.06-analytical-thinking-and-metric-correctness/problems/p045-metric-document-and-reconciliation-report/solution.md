## Approach

The project is the module in one place: define, compute, reconcile.

1. **Definition document.** A pure formatting function over the spec objects. Keep the header and the field order in
   constants and build the text from the specs: nothing about a particular metric is written in the function.
2. **Volume bridge.** The sets `T` (created in the period) and `C` (completed, started in the period); every job in only
   one of them gets one reason by its status or its dates; the counts per reason are the steps.
3. **Cash bridge.** Work value, then the seven named buckets of money, as in problem 44.
4. **One `bridge` formatter** checks that the running total reaches the end value and raises otherwise, so the report can
   never show a bridge that does not close.
5. **The report** puts both bridges together with the job ids behind each line, so every line is checkable.

The boundary jobs (created or started exactly at `1 Mar 00:00`, a payment in the last second of February) are in the data
to make the half-open rule visible in the numbers.

## Code

```python
import pandas as pd

HEADER = ["# QuickFix: metric definitions (v1)", "",
          "All dates are IST (UTC+05:30). A month is a half-open interval [first day, first day of next month).", ""]
LATE = "created before the month, started in it"
CASH_LABELS = [
    "completed in month, paid before the month",
    "completed in month, paid after the month",
    "completed in month, not paid yet",
    "paid in month, job completed earlier",
    "paid in month, job completed later or pending",
    "paid in month, other jobs",
    "refunds issued in month",
]


def definition_doc(specs):
    lines = list(HEADER)
    for m in specs:
        lines += [f"### {m.name}", f"- Question: {m.question}", f"- Unit: {m.unit}", f"- Date basis: {m.date_basis}",
                  f"- Includes: {m.includes}", f"- Excludes: {m.excludes}", ""]
    return "\n".join(lines)


def _bridge(start_label, start_value, steps, end_label, end_value):
    lines = ["step | change | running | check", " | ".join([start_label, "", str(start_value), ""]).rstrip()]
    running = start_value
    for label, change in steps:
        running += change
        lines.append(" | ".join([label, f"{change:+d}", str(running), ""]).rstrip())
    gap = running - end_value
    if gap != 0:
        raise ValueError(f"UNEXPLAINED {gap:+d}: bridge from {start_label} does not reach {end_label}")
    lines.append(" | ".join([f"= {end_label}", "", str(end_value), "OK"]))
    return lines


def _volume(jobs, start, end):
    created = (jobs["created_at"] >= start) & (jobs["created_at"] < end)
    started = (jobs["started_at"] >= start) & (jobs["started_at"] < end)
    in_c = started & jobs["status"].eq("completed")
    names = {"cancelled": "cancelled (never started)", "failed": "failed", "pending": "pending (no start date yet)"}
    ids = {}
    for r in jobs[created & ~in_c].itertuples():
        ids.setdefault("created in month, " + names.get(r.status, "started after the month"), []).append(int(r.job_id))
    late = [int(j) for j in jobs.loc[in_c & ~created, "job_id"]]
    steps = [(label, -len(v)) for label, v in sorted(ids.items())]
    if late:
        steps.append((LATE, len(late)))
        ids[LATE] = late
    return int(created.sum()), int(in_c.sum()), steps, {k: sorted(v) for k, v in ids.items()}


def _cash(jobs, pay, ref, start, end):
    done = jobs[jobs["status"].eq("completed") & (jobs["completed_at"] >= start) & (jobs["completed_at"] < end)]
    work = int(done["quote_total"].sum())
    p = pay.merge(jobs[["job_id", "status", "completed_at"]], on="job_id", how="left", validate="m:1")
    inside = (p["paid_at"] >= start) & (p["paid_at"] < end)
    on_done = p["job_id"].isin(set(done["job_id"]))
    before, after = p[on_done & (p["paid_at"] < start)], p[on_done & (p["paid_at"] >= end)]
    other = p[inside & ~on_done]
    earlier = other[other["completed_at"] < start]
    later = other[(other["completed_at"] >= end) | other["status"].eq("pending")]
    rest = other[~other.index.isin(earlier.index) & ~other.index.isin(later.index)]
    r_in = ref[(ref["refunded_at"] >= start) & (ref["refunded_at"] < end)]
    paid_total = p[on_done].groupby("job_id")["amount"].sum()
    unpaid_ids = done.loc[done["quote_total"] > done["job_id"].map(paid_total).fillna(0), "job_id"]
    unpaid = work - int(before["amount"].sum()) - int(p[on_done & inside]["amount"].sum()) - int(after["amount"].sum())
    amounts = [-int(before["amount"].sum()), -int(after["amount"].sum()), -unpaid, int(earlier["amount"].sum()),
               int(later["amount"].sum()), int(rest["amount"].sum()), -int(r_in["amount"].sum())]
    ids_of = lambda f: sorted(int(j) for j in f["job_id"].unique())
    ids = dict(zip(CASH_LABELS, [ids_of(before), ids_of(after), sorted(int(j) for j in unpaid_ids),
                                 ids_of(earlier), ids_of(later), ids_of(rest), ids_of(r_in)]))
    net = int(p.loc[inside, "amount"].sum()) - int(r_in["amount"].sum())
    return work, net, list(zip(CASH_LABELS, amounts)), ids


def _ids_block(ids, order):
    lines = ["Jobs behind each line:"]
    shown = [f"- {label}: {ids[label]}" for label in order if ids.get(label)]
    return lines + (shown or ["- none"])


def reconciliation_report(tables, month):
    start, end = pd.Timestamp(month[0]), pd.Timestamp(month[1])
    jobs, pay, ref = tables["jobs"], tables["pay"], tables["ref"]
    total, completed, steps, ids = _volume(jobs, start, end)
    order = [label for label, _ in steps]
    out = [f"# Reconciliation report: {month[0]} to {month[1]} (IST)", "",
           "## 1. Total volume against completed volume", ""]
    out += _bridge("total volume (created in month)", total, steps, "completed volume (started in month)", completed)
    out += [""] + _ids_block(ids, order) + [""]
    work, net, csteps, cids = _cash(jobs, pay, ref, start, end)
    out += ["## 2. Completed work against net cash", ""]
    out += _bridge("completed value (month)", work, csteps, "net cash (month)", net)
    out += [""] + _ids_block(cids, CASH_LABELS)
    return "\n".join(out)
```

## Complexity

O(n + m) for the tables (a few masks, one merge of payments to jobs, a few group-bys); the report text is O(number of lines).

## Another way

Make `definition_doc` and the metric table (problem 43) read the same `MetricSpec` objects, so the document and the
numbers can never drift apart. Add a second engine (SQL) that must reproduce the first bridge, and a third section called
"Open issues" for data gaps (failed jobs have no failure time; pending jobs have no start date), as the chapter does.
