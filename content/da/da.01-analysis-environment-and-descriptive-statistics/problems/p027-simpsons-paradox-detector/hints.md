## Hint 1

What two tallies do you need per `(group, treatment)`, and what other tallies per `treatment`? How will you know "every group prefers the same treatment"? A set of winners is one way.

## Hint 2

```text
cell[group][treatment] = [successes, rows]; total[treatment] = [successes, rows]
rates = successes / rows
group winner = "A" if rate A > rate B, "B" if B > A, "tie" otherwise
overall winner likewise
paradox = all group winners are the same one treatment (no ties) AND overall winner is the other one
```
