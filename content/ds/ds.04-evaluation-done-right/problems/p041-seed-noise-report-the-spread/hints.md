## Hint 1

Collect the scores in a list first. Which NumPy function gives the sample (not population) standard deviation?

## Hint 2

`scores = [run(s) for s in seeds]`, then `np.std(scores, ddof=1)`.
