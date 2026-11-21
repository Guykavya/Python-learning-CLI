# Roll back or forward, and the first five minutes

Chapter sections 12.4 (rollback and the database), 12.5 (deployment hygiene), 14.1 (runbooks), 14.2 (incidents and postmortems) and "Try it: first five minutes" and "Try it: roll forward or back?". It is 14:07. The alert `HighErrorRate` fires: **5xx at 30%** of requests. The last deployment, version **1.4.2**, finished at 13:55. It contained a code change and a database migration. You are on call.

In `answer.md` explain (about 300 to 450 words):

1. **The first five minutes**, in order: what you do, and why in that order. Use the words *mitigate*, *stabilise*, *communicate*, *request id*. (Four or five steps.)
2. **The decision rule**: when do you **roll back**, and when must you **roll forward** or restore instead? What must you know about the migration of 1.4.2 to decide? Name the pattern that makes rollbacks safe.
3. **What if the error rate stays at 30% after the rollback?** What have you learned, and what do you do next?
4. What to do about **people**: who leads, what you write down while you work, and what you tell users and the team.
5. The sections of a **blameless postmortem**, and the one that matters most.
6. Name **two preparations** made *before* the incident that made the response fast (think of the chapter's deployment script and runbook).

## Example

A good first step: "1. Check whether a deployment happened in the last 30 minutes (here yes: 1.4.2 at 13:55). A recent change is the most likely cause, so I will undo it first."
