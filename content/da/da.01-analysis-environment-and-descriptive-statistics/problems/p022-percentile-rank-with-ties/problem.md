# Percentile rank with ties

Chapter section 12.5. The percentile rank of a score is the percent of the data below it **plus half of the percent equal to it** (a tie counts half, so a score sitting in a crowd gets the middle of the crowd).

```python
def percentile_rank(values, score):
    below = sum(1 for x in values if x < score)
    equal = sum(1 for x in values if x == score)
    return 100 * (below + 0.5 * equal) / len(values)


marks = [50, 60, 60, 70, 70, 70, 80, 90]
for score in [60, 70, 55, 90]:
    print(f"score {score}: percentile rank {percentile_rank(marks, score):.1f}")
```

Hand-trace the program and write the four printed lines in `answer.txt`. Work out `below`, `equal` and the percentage for each score, and then be careful with the **rounding to one decimal**: Python rounds the exactly representable value `56.25` to the nearest even last digit, not always upward.

## Answer format

Four lines, `score S: percentile rank R`, one decimal.

## After you answer

- Why is the rank of 55 (a score that nobody got) not 0 or 100?
- What would the formula give for the lowest score if there were no ties? For the highest?
