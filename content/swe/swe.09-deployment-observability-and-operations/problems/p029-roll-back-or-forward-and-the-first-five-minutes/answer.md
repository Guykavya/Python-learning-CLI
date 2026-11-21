## Model answer

**The first five minutes.**
1. **Look at what changed.** 5xx started after the deployment of 1.4.2 at 13:55 (12 minutes ago): a recent change is the most likely cause.
2. **Mitigate first, diagnose second.** Roll back: `./deploy.sh 1.4.1` (the image still exists, nothing is rebuilt; chapter 12.3). A rollback takes a minute, finding the cause may take hours, and users are being hurt now. Before touching anything, note the time and what you are doing.
3. **Communicate.** Tell the team and, if users are affected, post a short status message ("investigating elevated errors since 13:55, rolling back"); repeat at regular intervals even if there is no news.
4. **Verify the effect.** Watch the dashboards (5xx ratio, p95) and `/readyz`; the error rate should fall within a minute or two.
5. **Then investigate with the pressure off.** Take one failing **request id** from a user report or from `jq 'select(.level=="ERROR")'`, follow it through nginx and the app logs, and read the traceback (chapter 8.4). Keep the failed release folder or container logs as evidence.

**The decision rule.** Roll back when the previous version still works with the current database: the migration of 1.4.2 was **additive** (expand: a nullable column, a new table) and old code ignores it. If 1.4.2's migration **renamed, dropped or transformed** data in place, old code meets a schema or data it cannot read, and rolling back makes things worse (it can write rows in the old shape and corrupt data): then **stop the damage** (feature flag off, maintenance page, or a fast fix) and **roll forward** with a fix that handles both shapes, restoring from a backup only if data is truly damaged and you accept losing what was written since. The pattern that makes rollbacks safe is **expand and contract**: add first, migrate the code, remove the old shape in a later release (chapter 12.4).

**If the error rate stays at 30%.** Then the deployment was not the cause, and you lost two minutes, not twenty. Widen the search: dependencies (`/readyz` lists which one fails: database, Redis), the provider status pages, traffic spikes, a full disk, certificates. Escalate if not mitigated in 15 minutes (the runbook says to whom).

**People.** One person **leads** (decides and keeps the timeline); others help with specific tasks. Write what you do and when, as you do it (UTC times). Change one thing at a time and note it. Do not panic-deploy untested fixes.

**Postmortem.** Blameless, about the system and not the person: summary, timeline (UTC), cause (and why our checks did not stop it), what went well / badly / where we got lucky, and **actions** with an owner and a date. The **actions** matter most: a test, an alert, a runbook step, a limit, and actually doing them.

**Preparations that made it fast.** A deployment script that records the previous version and rolls back by itself with immutable, versioned images; health checks and configuration validated at start-up; JSON logs with request ids; an alert with a **runbook** whose first steps are "was there a deployment in the last 30 minutes? roll back first"; and a backup that had been restored in a drill.

**Checklist: your answer should mention**
- [ ] a recent deployment is the first suspect; mitigate (roll back) before diagnosing
- [ ] communicate to the team and users, with updates at regular intervals
- [ ] verify with dashboards after the rollback, then investigate with a request id and the logs
- [ ] roll back only if the migration was additive; destructive or in-place migrations mean roll forward (or restore), and expand and contract is the pattern
- [ ] if errors continue after the rollback, the deployment was not the cause: widen the search, escalate on time
- [ ] one leader, a written timeline, one change at a time
- [ ] blameless postmortem sections, with owned, dated actions as the most important part
- [ ] preparations: versioned images, rollback script, health checks, JSON logs and request ids, runbook, tested backups
