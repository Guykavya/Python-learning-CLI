## Model answer

**1. The choices.**
- **Assigning a task under the WIP limit: C.** The rule says "at most 3 open tasks". If both sides of a partition accept assignments, each can see "2 open" and add one: the user ends with 4. The check needs an up-to-date count, so the node that cannot reach the others (or a majority) **refuses**. The user sees an error ("could not assign, try again"). An error is better than breaking a business rule.
- **The activity feed: A.** A feed that is a few seconds or minutes behind is harmless, and a feed that *disappears* during an incident is a worse experience. Serve what the node has (it may be **stale**); new events appear when the partition heals. The user sees a slightly old feed, maybe with a "may be out of date" hint.
- **The unread counter: A.** An approximate badge that converges later is fine. Use counters that **merge** (each node counts its own increments and the totals are added), and a periodic recount repairs drift. The user may see 3 where it should be 4 for a while.
- **Billing: C.** Never charge twice and never guess. During a partition **refuse** or mark the payment **pending** and reconcile later; every charge carries an **idempotency key** so that a retry cannot double-charge. The user sees "payment pending", not a silent duplicate.

**2. Conflicts after an A choice.** Writes accepted on both sides must be merged when the network heals. **Last write wins** (the newest timestamp is kept) is simple but **silently discards** the other write: if Ana renames a task to "Docs" on one side and Ben to "Documentation" on the other, one rename is lost without any message, and clocks that disagree can even keep the older one. Better: merge rules where possible (counters add, sets union), version vectors or versions that detect the conflict, or ask the user.

**3. CAP and PACELC.** CAP only speaks about the partition. **PACELC** adds the normal case: *if there is a Partition, choose Availability or Consistency; Else, choose Latency or Consistency.* Even with a healthy network, waiting for every replica to confirm a write (consistency) is slower than answering at once (latency): it is the replica-lag trade-off in one sentence.

**4. Consistency levels.** Strong (a bank balance, a single primary), **read-your-writes** (you see your own writes), monotonic reads (time never goes backwards), eventual (replicas, search index, likes). Read-your-writes is right for **a user who has just edited a task or a profile**: if the next page load hits a lagging read replica and shows the old value, the user thinks the save failed. Route that user's reads to the primary for a short while, or pin them to the replica that has their write.

**5. Taskboard today** is one SQLite file: a single node has no partitions to survive and is strongly consistent. To grow: move to PostgreSQL (primary plus replica), add read-your-writes routing for the person who just edited, keep the outbox in the primary's transaction, and move on only when measurements say so.

**Checklist: your answer should mention**
- [ ] WIP-limit assignment and billing choose C (refuse or mark pending; never exceed the limit, never double-charge; idempotency key)
- [ ] feed and unread counter choose A (stale is fine; counters that merge; recount repairs drift)
- [ ] what the user sees for each choice (an error / pending versus a slightly old value)
- [ ] last write wins silently loses a write; merge rules, versions or asking the user are better
- [ ] PACELC: with no partition the trade-off is latency versus consistency (waiting for replicas)
- [ ] read-your-writes after an edit, and how to provide it
- [ ] Taskboard on one SQLite file is a single strongly consistent node; first step is PostgreSQL primary plus replica
