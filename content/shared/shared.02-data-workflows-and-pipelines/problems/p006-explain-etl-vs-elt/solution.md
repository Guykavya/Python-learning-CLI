## Approach

The model answer is in `answer.md`. The choice is decided by two facts in each scenario:

| Question | Scenario 1 | Scenario 2 |
|---|---|---|
| Do the rules change, and must history be redone? | yes, often | no, fixed format |
| Can the source be read again later? | no, only 90 days | does not matter |
| May the destination see the raw data? | yes (our own database) | **no** (emails, amounts) |
| Can the destination transform? | yes, SQL | no |
| Choice | **ELT** | **ETL** |

## Check your answer

- Did each choice use reasons from the scenario (changing rules, the 90-day limit, the contract, the courier's lack of SQL), not textbook phrases like "ELT is modern"?
- For scenario 1, did you say that the raw layer is the only copy of history because the API forgets?
- For scenario 2, did you say that removing emails must happen *before* the data leaves, so ELT would break the contract on load?
- Did you describe the layers with real column names or an example row?
- Did you name a real cost for each (raw layer is sensitive / large; a transform bug reaches the courier) and a concrete mitigation (access rules, retention; output checks, quarantine)?

## Another way

Many real systems mix the two: they keep a raw copy for themselves (the "L" of ELT on their
own side) and run an ETL step for every external consumer. Scenario 2 could be built on top
of scenario 1's staging table: `SELECT id, city, ... FROM stg_orders WHERE status = 'shipped'`,
written to CSV. That is still ETL from the courier's point of view, because the courier only
ever receives transformed rows.
