## Approach

Track the watermark of each loader and the filter it turns into.

| Run | source (id: t) | `gt` filter -> ids | `ge` filter -> ids | `overlap` filter -> ids |
|---|---|---|---|---|
| 1 | 1:100, 2:105 | none -> [1, 2] | none -> [1, 2] | none -> [1, 2] |
| 2 | + 3:105, 4:107 | t > 105 -> [4] | t >= 105 -> [2, 3, 4] | t > 102 -> [2, 3, 4] |
| 3 | unchanged | t > 107 -> [] | t >= 107 -> [4] | t > 104 -> [2, 3, 4] |
| 4 | 2 becomes 109, + 5:103 | t > 107 -> [2] | t >= 107 -> [2, 4] | t > 104 -> [2, 3, 4] |

After run 1 every watermark is 105. After runs 2 and 3 it is 107, after run 4 it is 109.

`changed`:

- Run 1: both ids are new: 2.
- Run 2: `gt` only gets 4 (new): 1. `ge` and `overlap` get 2 (unchanged, 0), 3 and 4 (new): 2.
- Run 3: nothing changed in the source, so every re-fetched row counts 0. `gt` fetched nothing
  and keeps 107; `ge` re-fetches 4 (it equals the watermark); `overlap` re-fetches everything in
  its 3-minute window.
- Run 4: 2 changed (105 -> 109) and is caught by everyone: 1. Order 5 (103) is older than every
  filter's lower bound (107 for `gt`/`ge`, 104 for `overlap`), so nobody sees it.

Final check: `gt` never stored order 3 (the late row with t = 105 = its watermark) nor 5.
`ge` and `overlap` caught 3 but also missed 5. Nobody has stale data, because every change
moved `updated_at` forward past the watermarks.

## Full output

```
-- run 1
gt [1, 2] 2 105
ge [1, 2] 2 105
overlap [1, 2] 2 105
-- run 2
gt [4] 1 107
ge [2, 3, 4] 2 107
overlap [2, 3, 4] 2 107
-- run 3
gt [] 0 107
ge [4] 0 107
overlap [2, 3, 4] 0 107
-- run 4
gt [2] 1 109
ge [2, 4] 1 109
overlap [2, 3, 4] 1 109
gt missing [3, 5] stale []
ge missing [5] stale []
overlap missing [5] stale []
```

## What this shows

- `>` is exact only if no row can ever appear later with a timestamp equal to the watermark.
  Real databases commit transactions in a different order than their timestamps, so that is
  rarely guaranteed.
- `>=` (or an overlap window) trades a few **re-fetched rows on every run** for safety. That is
  only acceptable because the write is an idempotent upsert: `changed` stays 0 for repeats.
- An overlap window covers late data only up to its width. Data later than that (order 5) needs a
  periodic full reload or a backfill (p024).

## Complexity

Each run costs one pass over the source here. In a real API, `ge` re-reads the rows at the
boundary and `overlap` re-reads every row in its window on every run.

## Another way

Check yourself by adding `print(loader.mode, loader.table)` at the end of `run`. A safer design
uses a **cursor that the server orders strictly**, such as `(updated_at, id)` pairs or a change
sequence number, so "after the last one I saw" is never ambiguous.
