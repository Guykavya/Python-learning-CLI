## Hint 1

Which function in `itertools` is the lazy cousin of the slice `[start:stop]`? Does it accept negative numbers?

## Hint 2

`islice(it, start, stop)` skips `start` items, then gives items until position `stop`. Wrap the result in `list`.

## Hint 3

```
from itertools import islice
return list(islice(iterable, start, stop))
```
