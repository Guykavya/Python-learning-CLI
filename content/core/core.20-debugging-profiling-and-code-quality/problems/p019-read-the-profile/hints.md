## Hint 1

Read one row as a sentence: "`find_user` was called 100000 times; its own lines took 0.392 s in
total; from entering to leaving it took 0.392 s in total". Now do the same for `build` and
`main`. Which of the two columns tells you where the work is **really** done?

## Hint 2

For questions 3 to 5, do the arithmetic:

```
real per call     = tottime / ncalls
share of the run  = cumtime / total time
best saving       = cumtime * (1 - 1/speedup)
pick the function with the biggest OWN time (tottime) that you can make do less work
```

Then ask what `find_user` does on each call, and which data structure answers "have I seen this
name?" in one step.
