## Hint 1

Five strategies, five different pandas methods from section 11.2. Which method does each word in the table correspond to? And which one needs a number computed from the *known* values first?

## Hint 2

```text
"drop"        -> s.dropna()
"zero"        -> s.fillna(0)
"ffill"       -> s.ffill()
"interpolate" -> s.interpolate()
"median"      -> s.fillna(s.median())     (median skips the gaps by itself)
anything else -> raise ValueError(...)
```
The leading-gap rule needs no extra code: `ffill()` and `interpolate()` already leave a gap at the start alone.
