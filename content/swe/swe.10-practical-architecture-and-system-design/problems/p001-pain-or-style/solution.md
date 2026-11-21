## Approach

| # | Complaint | Verdict | Why |
|---|---|---|---|
| 1 | "does not follow clean architecture" | **style** | no bug, no cost, no measurement |
| 2 | one rule in 1 of 3 entry points, a customer got a 4th task | **pain**, `service-layer` | duplicated rule that already caused a bug; one function per use case fixes it |
| 3 | one `if` needs a client, a file and 40 lines of set-up | **pain**, `repository` | rules and storage are tangled, so testing the rule needs the database; a fake repository lets the rule run in microseconds |
| 4 | a failed request commits later | **pain**, `unit-of-work` | the transaction is shared and by convention; an object that owns it makes the rollback automatic |
| 5 | "we might switch databases" | **style** (speculation) | the SQL dialects differ anyway, so empty interfaces written today would not save you; wait for the pain or a decision date |
| 6 | e-mail for a rolled-back change, or lost | **pain**, `events-outbox` | commit and e-mail cannot be atomic; save the intention in the same transaction and deliver it later |
| 7 | teams blocked, very different load | **pain**, `separate-services` | the reasons to split are about **people and load** (chapter 11.4) |
| 8 | status rules scattered next to SQL | **pain**, `domain-model` | rules about one object's state belong with that object, testable with no set-up |

The answers to the two questions: for 5, write the code you need now, keep SQL in one place if it already hurts, and add the interface when a second implementation or a migration date exists. 3 is a pain about **where the data comes from** (the rule needs a database to run: repository), 8 is a pain about **where the rules live** (scattered: domain model); the cure for 8 also removes the set-up cost, because a domain rule needs nothing at all.

## Cost

Reading only. The habit it builds: every layer in a review has to answer "which pain, with what evidence?".

## Another way

Write your own **pain log** (chapter 3.4): one row per pain, with evidence you can re-check (a failing test, a `grep`, a timing, a line count). If you cannot fill a row for a layer, you may not need that layer yet.
