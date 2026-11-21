## Hint 1

Ask of each item: "can this number ever go **down** (apart from a restart)?" If never, it is a counter. If yes, is it one current value (gauge) or a whole distribution of values from which you want percentiles (histogram)?

## Hint 2

Write beside each item the word you would put in front of it in a graph title: "rate of ...", "current ...", or "95th percentile of ...". "Rate of" means counter, "current" means gauge, "percentile of" means histogram.

```text
total so far (requests, errors, bytes)      -> counter
level right now (queue, memory, in flight)  -> gauge
distribution (durations, sizes)             -> histogram
```
