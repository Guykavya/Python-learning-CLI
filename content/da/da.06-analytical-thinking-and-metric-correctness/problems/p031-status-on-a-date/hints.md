## Hint 1

Take the jobs one at a time and go down the five rules until one is true. For each timestamp ask: is it present, and is
it `<=` the moment `AT` (12:00 on 10 February)? What does a comparison with a missing time give? For the counts, how
does `value_counts().sort_index()` order the states?

## Hint 2

```text
101: created Feb 01 (fine), no cancel, completed 15:00 > AT (not yet), started 12:00 <= AT  -> in progress
102: created Feb 09, cancelled exactly at AT  -> cancelled
103: created exactly at AT (not after)       -> no event yet -> waiting
104: created one second after AT             -> not yet created
105: completed 11:59 <= AT                   -> done
106: started Feb 12 > AT                      -> waiting
counts sorted by name: cancelled, done, in progress, not yet created, waiting
open = waiting or in progress -> ids 101, 103, 106
the last line: completed_at > AT is True for two jobs (NaT gives False); 3 jobs have a completed_at
```
