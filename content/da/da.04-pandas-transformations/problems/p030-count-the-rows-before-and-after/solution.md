## Approach

The model answer in `answer.md` builds the argument from the **grain**: once you know what one row of each table is, you
can predict the row count of a merge, and any difference is a bug. The two merges in the question show all three
failure modes: the default inner join loses lines, a duplicated product id would duplicate lines, and joining
`returns` on half of its key fans out. Rate your answer against the checklist at the end of `answer.md`.

## Complexity

The checks are almost free: `len` is O(1), `validate` is one uniqueness check O(n), a total is O(n). They cost far less
than a wrong number in a report.

## Another way

Wrap the habits in one helper (Ch. 14 builds `safe_merge`): it takes `how`, `validate` and a measure column, merges,
checks the row count for a left join, reports unmatched keys from the indicator and checks that the measure total is
unchanged.
