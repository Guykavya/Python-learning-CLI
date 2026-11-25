## Hint 1

Which jobs belong to the data at all (compare `created_at` with the cut)? How old is a job at the cut, and what exact
comparison says "at least 14 days old"? What is the share of completed jobs in a group, and what should you return when
the group is empty?

## Hint 2

```text
cut = pd.Timestamp(cut)
seen   = jobs where created_at < cut
mature = seen where created_at <= cut - Timedelta(days=min_age_days)
naive  = share of status == "completed" in seen
rate   = same share in mature, or None when mature is empty
return {"naive": naive, "mature": rate, "jobs": len(seen), "mature_jobs": len(mature)}
```
