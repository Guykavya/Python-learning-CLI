## Hint 1

`cycle(x)` never ends. So what must you add around it, so your function does end?

## Hint 2

`list(islice(cycle(labels), n))`. Think about the empty list: `cycle([])` ends at once, so you get an empty result.

## Hint 3

```
from itertools import cycle, islice
return list(islice(cycle(labels), n))
```
