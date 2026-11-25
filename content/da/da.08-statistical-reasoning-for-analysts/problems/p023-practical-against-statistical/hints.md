## Hint 1

You answer two independent questions about the same interval: where is it relative to the MEI, and where is it relative to zero. Which comparisons use strict inequalities?

## Hint 2

```text
label: if lo > mei -> worth it ; elif hi < mei -> not worth it ; else inconclusive
significant = lo > 0 or hi < 0
return label, significant
```
