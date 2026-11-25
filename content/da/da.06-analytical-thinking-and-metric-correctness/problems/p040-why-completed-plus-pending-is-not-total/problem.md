# Why completed plus pending is not total

Chapter section 12. In February the dashboard of QuickFix showed:

| Number | Date basis | Status filter | Value |
|---|---|---|---|
| total volume | `created_at` in Feb | none | 895 |
| completed volume | `started_at` in Feb | `completed` | 809 |
| pending volume | `started_at` in Feb | `pending` | 0 |

A manager asks: "809 + 0 is not 895. Is a job missing from the database?" Explain in `answer.md` (about 300 words) why
there is no error, using the numbers of the chapter's bridge (895, then -87, -84, -13, +98, then 809):

1. Name **three different reasons** why the parts do not add up to the total, and say for each one whether it makes the
   parts **bigger or smaller** than the total.
2. Explain why the **pending volume is exactly zero**, not just small.
3. Why does a net gap of 86 jobs hide effects that are bigger than 86?
4. Say what the **dashboard** should show so that "total = part + part + ..." is true by construction, and what a
   **bridge** adds to the explanation.

## Example

A start: "Nothing is missing. The three numbers count different groups of jobs. The total counts the jobs created in
February, whatever their status. The 'completed' number counts only completed jobs, and it places them by the date they
started, so it contains jobs that were created in January and leaves out jobs that..."
