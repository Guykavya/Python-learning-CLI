## Hint 1

Make a small table on paper with one column per loader and three rows: `wm`, `table` and the
current `source`. For each run, first write the filter as a number range (for example "`gt`
with wm 105 means t > 105"), then list which source ids fall in it, sorted. Which ids have
`updated_at` exactly equal to a watermark at some point, and which loaders can still see them?

## Hint 2

`changed` counts only ids whose stored value differs from the source (new ids, or a different
`updated_at`). A re-fetched row that did not change adds 0. The watermark only ever becomes the
max of what was fetched in **this** run; when nothing is fetched, it stays.

```
run 1: every wm is None          -> all ids [1, 2]; wm = 105 for all three
run 2: source {1:100, 2:105, 3:105, 4:107}
       gt:  t > 105   -> ?        ge: t >= 105 -> ?        overlap: t > 102 -> ?
run 3: same source, wm 107 for all      gt: t > 107   ge: t >= 107   overlap: t > 104
run 4: source adds 2:109 and 5:103; same three filters as run 3
final: missing = source ids never stored; stale = stored value != source value
```
