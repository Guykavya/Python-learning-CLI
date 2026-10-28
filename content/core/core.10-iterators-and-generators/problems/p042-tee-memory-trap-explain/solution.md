## Approach

The key idea is the buffer. `tee` cannot rewind the source, so it remembers the items that some
copy has read and another copy has not. Memory use is therefore set by how far apart the copies
get, not by the size of the data. Used side by side, the buffer stays tiny. Used one after the
other, the buffer becomes a full copy of the data.

## Model answer

See `answer.md`.

## Complexity

Extra memory of `tee` is O(d), where d is the largest gap (in items) between the fastest and the
slowest copy. Reading one copy fully before the other makes d = n.

## Another way

Picture two people reading one book that only one of them can hold. The first reads aloud, and a
helper writes every sentence on cards for the second one. If the second reader keeps up, the helper
needs only a few cards. If the second reader starts after the first has finished, the helper has
copied the whole book.
