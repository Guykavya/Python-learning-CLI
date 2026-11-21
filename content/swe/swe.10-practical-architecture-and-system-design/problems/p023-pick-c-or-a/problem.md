# Pick C or A

Chapter sections 15.3 (consistency, in plain words), 15.5 (CAP: what happens when the network splits), 15.6 (where Taskboard sits) and "Try it: pick C or A". Distributed data stores have several copies, and the network between them can break. When a **partition** happens, a system must choose: **C**onsistency (every read gets the latest write or an error: a node on the minority side must *refuse* to answer) or **A**vailability (every request to a working node gets an answer, even if stale, and writes are accepted on both sides; after healing, conflicts must be resolved). Partitions are not optional in real networks, so the real choice is "C or A **during** a partition". Neither is better; you choose from the business.

For each of these four features of Taskboard, choose **consistency or availability during a network partition**, and say **what the user sees**:

1. **Assigning a task** under the work-in-progress limit (a user may have at most 3 open tasks).
2. The **activity feed** of a project.
3. The **unread counter** (the badge with a number).
4. **Billing**: charging a customer's card for the monthly plan.

In `answer.md` write about 350 to 500 words, covering:

1. For each feature: the **choice** (C or A), **why**, and **what the user sees** during the partition.
2. For the ones that choose **A**: what **conflict handling** you need after the partition heals, and what "last write wins" can silently do (give an example).
3. The difference between **CAP** (during a partition) and **PACELC** ("else", in normal operation): what is the trade-off when there is no partition?
4. The **consistency levels** the chapter lists (strong, read-your-writes, monotonic, eventual): give one place in Taskboard where read-your-writes is the right level and say why.
5. Where does **Taskboard today** (one SQLite file) sit, and what is the first step to grow?

Use the words *partition*, *stale*, *refuse*, *eventual*, *last write wins*, *idempotent*.

## Example

A good first line: "Assigning under the WIP limit needs **C**: two nodes that each accept an assignment during a partition could both give a user a 4th task; I prefer an error ('try again') to breaking the rule."
