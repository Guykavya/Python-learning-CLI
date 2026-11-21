## Approach

The model answer is in `answer.md`. The whole thing in one rule from the chapter: **mitigate first, diagnose second**. A rollback is fast, safe by design (immutable images, a script that records the previous version) and informative: if it does not help, you have ruled out the deployment at the price of two minutes. The one exception is a release whose migration cannot be undone; for that you must know, **before** the incident, whether this release can be rolled back (the release plan says so), and prefer a roll forward when it cannot.

## Cost

Nothing to build; the cost is practice. The chapter's game-day drills (15.4) and the restore drill (13.2) are how the first five minutes become routine.

## Another way

Write your own one-page runbook for `HighErrorRate` from the chapter's example and compare: the first two minutes are "was there a deployment? roll back first", then dashboards, then one request id, then dependencies, then mitigation, then escalation after 15 minutes. Problem p015 gives you the tool for "follow one request id", and p026 the case where the rollback is not enough.
