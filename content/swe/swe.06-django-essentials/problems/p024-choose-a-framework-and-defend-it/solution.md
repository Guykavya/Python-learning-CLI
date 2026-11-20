## Approach

Use the five questions of section 19.2 to turn each job into facts, then choose, then state the cost and the trigger.

```text
B  program user, I/O waiting, no admin/forms     -> FastAPI (or DRF if the team is already on Django)
D  people + staff, central data, roles, pages    -> Django
G  existing working Django, one live feature     -> keep Django + Channels or a small FastAPI service
```

The full model answer and a checklist are in `answer.md`. The key sentence: **a choice is defended by the job, the cost you accept and the measurement that would change it.**

Example of one sentence per part for job D: "Choice: Django, because the admin, permissions and forms are the product. Cost: heavier and mostly synchronous. Trigger: a single-page front end that only needs an API."

## Complexity

Not applicable; this is a reasoning exercise.

## Another way

Write the table of section 19.1 for your own project: for each row (admin, auth, ORM, async, validation) mark "needed", "nice" or "not needed". Count what you would have to build yourself in each framework. The framework with the fewest needed items to build is usually the best fit, and the same table is your defence.
