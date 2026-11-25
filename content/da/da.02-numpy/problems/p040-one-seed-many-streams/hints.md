## Hint 1

Compare the two printed lists element by element. Which worker of run 101 matches which worker of run 100? Why must that happen, given how proposal A builds the seeds?

## Hint 2

A Generator is an object that holds a **state** and moves it forward with each draw. If you make a copy of it, what does the copy draw next? What happens when 8 workers all start from the same state?

## Hint 3

```text
A: seeds 100..107 vs 101..108 -> 7 seeds shared -> streams repeat across runs
B: 8 copies of one state      -> 8 identical streams
C: SeedSequence(seed).spawn(8) -> 8 different, non-overlapping children, same every time for the same seed
worker: one generator, kept and passed as an argument; no new default_rng(fixed) inside loops; no np.random.seed
```
