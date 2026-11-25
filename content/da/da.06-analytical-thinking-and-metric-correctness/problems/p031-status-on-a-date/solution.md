## Approach

Apply the rules in the written order for each job.

1. `101`: created long before, no cancellation, `completed_at` 15:00 is after `AT`, `started_at` is exactly `AT`, so `in progress`.
2. `102`: cancelled exactly at `AT`, the event has happened, `cancelled`.
3. `103`: created exactly at `AT` is not "after", it has no other events, so `waiting`.
4. `104`: created one second after `AT`, `not yet created`.
5. `105`: completed at 11:59, `done`.
6. `106`: its start (12 February) is after `AT`, so `waiting`.
7. State counts, sorted by name: 1 cancelled, 1 done, 1 in progress, 1 not yet created, 2 waiting.
8. Open jobs (waiting or in progress): `[101, 103, 106]`.
9. Completed after `AT`: jobs 101 and 106, so 2; three jobs have a `completed_at`. Today's `status` of 101 and 106 is
   probably `completed`, yet at `AT` they were not done.

## Output

```text
101 in progress
102 cancelled
103 waiting
104 not yet created
105 done
106 waiting
{'cancelled': 1, 'done': 1, 'in progress': 1, 'not yet created': 1, 'waiting': 2}
[101, 103, 106]
2 3
```
