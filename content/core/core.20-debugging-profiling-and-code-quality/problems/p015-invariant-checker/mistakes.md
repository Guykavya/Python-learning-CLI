- Stopping at the first problem (`assert` or `return`). The task wants every problem.
- Skipping the amount of an entry that has a problem. The balance then drifts away from what
  really happened, and later messages show wrong numbers.
- Comparing each date with the **first** date or the largest date seen. The rule here is "not
  before the previous entry".
- Flagging equal dates. Two entries on the same day are fine; only an earlier date is wrong.
- Reporting `balance <= 0`. Exactly 0 is allowed.
- Using a list for seen ids. It works but makes the loop O(n^2) for large ledgers.
- Converting dates with `int(date.replace("-", ""))` or splitting them: correct but unneeded;
  ISO date strings already compare correctly.
