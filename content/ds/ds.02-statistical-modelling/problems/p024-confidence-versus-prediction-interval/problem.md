# Confidence versus prediction interval

Chapter section 10. A model of flat price (lakh rupees) on floor area was fitted twice on **synthetic** data: once with 100 flats and once with 10,000 flats from the same world (price = 5 + 0.03 * area + noise with sd 4, area from 500 to 1,500 sq ft). For a flat of **1,000 sq ft** the code below printed:

```python
sf = res.get_prediction(pd.DataFrame({"area": [1000.0]})).summary_frame(alpha=0.05)
print(sf.round(2).to_string())
```

```text
n = 100
    mean  mean_se  mean_ci_lower  mean_ci_upper  obs_ci_lower  obs_ci_upper
0  35.64      0.4          34.85          36.42         27.75         43.52
n = 10000
    mean  mean_se  mean_ci_lower  mean_ci_upper  obs_ci_lower  obs_ci_upper
0  35.03     0.04          34.96          35.11         27.28         42.78
```

Write your answer in `answer.md`:

1. What does the **mean confidence interval** (`mean_ci_*`) describe, and what does the **prediction interval** (`obs_ci_*`) describe?
2. A buyer asks "what will **my** 1,000 sq ft flat cost?" and an analyst asks "what is the **average** price of 1,000 sq ft flats?" Which interval answers which question?
3. Going from 100 to 10,000 flats, one interval shrank a lot and the other hardly changed. Which is which, and **why**?

## After you answer

Compare with the model answer and tick the checklist for the points you made.
