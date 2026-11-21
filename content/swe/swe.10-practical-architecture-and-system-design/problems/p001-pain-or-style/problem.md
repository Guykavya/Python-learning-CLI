# Pain or style?

Chapter sections 1.3 (the rule: pain first, layer second), 1.4 (a ladder from pain to remedy) and "Try it: pain or style?". Before you add a layer you must be able to point at a **concrete pain**: something you have seen, with evidence. A complaint that has no bug, no cost and no measurement is a **style** preference, and the answer is "not yet".

The ladder of the chapter, from the smallest remedy to the largest:

| Pain you can point at | Smallest remedy (write this word) |
|---|---|
| The same rule is copied into several routes and drifts apart | `service-layer` |
| Business code is full of SQL; tests of a rule need a real database | `repository` |
| Several writes must succeed or fail together; a failed request leaves half a change behind | `unit-of-work` |
| Rules are scattered over `if` statements next to the data they protect | `domain-model` |
| Something must happen *because* something else happened, and it must not be lost or sent twice | `events-outbox` |
| One team cannot deploy without waiting for another; one part needs 50 servers and the rest needs 1 | `separate-services` |

For each complaint about the Taskboard codebase, write `style` if it is not (yet) a pain, or `pain` followed by the remedy word.

1. "My routes do not follow clean architecture."
2. "The rule 'a user may have at most 3 open tasks' is checked in `POST` and forgotten in `PATCH` and in the reopen path; last week a customer got a 4th task."
3. "To check the work-in-progress rule I need a web client, a temporary database file and 40 lines of set-up, and the rule itself is one `if`."
4. "A request that fails after an insert leaves that insert pending, and the next successful request commits it."
5. "We might move from SQLite to PostgreSQL next year, so I will put an interface in front of every query now."
6. "When a task is assigned an e-mail must go out. Today a rolled-back assignment still sends the e-mail, and a failing provider loses it."
7. "The reporting team waits for the payments team on every release, and image resizing needs 50 servers while the rest of the app needs 1."
8. "The status rules (who may move from `todo` to `doing`, what reopening needs, what clears `completed_at`) are spread over five functions, each next to its own SQL."

## Answer format

Write exactly eight lines, one per complaint, in this form (number, colon, space, then `style` or `pain` and the remedy word):

```text
1: style
2: pain service-layer
...
```

## After you answer

- Complaint 5 sounds responsible. What would you do instead of writing the interface now, and when would you change your mind?
- Complaints 3 and 8 both mention testing a rule. What is the difference between the pain each one describes?
