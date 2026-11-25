# Trace `compare_centres`

Chapter section 10.6. Two rules of thumb decide whether the mean and the median tell the same story:

- `skew_hint` computes `gap = (mean - median) / pstdev` (population standard deviation) and calls the data right-skewed when `gap > 0.1`, left-skewed when `gap < -0.1`, else roughly symmetric;
- `compare_centres` says `"use median"` when the mean and the median differ by more than 10% of the median, else `"either is fine"`.

```python
import statistics


def skew_hint(values):
    mean, median = statistics.fmean(values), statistics.median(values)
    spread = statistics.pstdev(values)
    gap = (mean - median) / spread if spread else 0.0
    if gap > 0.1:
        return gap, "mean above median: right-skewed (tail to the high side)"
    if gap < -0.1:
        return gap, "mean below median: left-skewed (tail to the low side)"
    return gap, "mean and median close: roughly symmetric"


def compare_centres(values):
    mean = statistics.fmean(values)
    median = statistics.median(values)
    verdict = "use median" if abs(mean - median) > 0.10 * abs(median) else "either is fine"
    return {"mean": mean, "median": median, "verdict": verdict}


for name, data in [("symmetric", [1, 2, 3, 4, 5]),
                   ("right tail", [100, 101, 102, 103, 110]),
                   ("left tail", [1, 8, 9, 9, 10])]:
    gap, text = skew_hint(data)
    info = compare_centres(data)
    print(f"{name}: gap={gap:.2f}")
    print(f"  {text}")
    print(f"  mean={info['mean']:.2f} median={info['median']:.2f} -> {info['verdict']}")
```

Hand-trace the program and write the nine lines it prints in `answer.txt`. Numbers use two decimals, so compute the standard deviation carefully: the population `pstdev` divides the sum of squared deviations by `n`, not `n - 1`.

## Answer format

Nine lines: for each of the three datasets, one `name: gap=...` line followed by two indented lines (two spaces).

## After you answer

- For `"right tail"` the two rules disagree. Which one calls it skewed, which one says either centre is fine, and why does that happen (compare the size of the gap in standard deviations with the size relative to the median)?
- Which rule is better when all values are large and close together? When they are near zero?
