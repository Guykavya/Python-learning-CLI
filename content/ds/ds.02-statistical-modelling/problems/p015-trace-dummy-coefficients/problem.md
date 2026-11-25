# Trace dummy coefficients

Chapter sections 6.3 and 7.4. A model `log(wage) ~ experience + C(city)` with baseline city **Delhi** gave these coefficients. The intercept is the prediction for a Delhi worker with 0 years of experience; each city coefficient is the **difference from Delhi**.

```python
coefs = {"Intercept": 10.20, "experience": 0.025, "Mumbai": 0.12, "Pune": -0.10}
years = 10

for city in ["Delhi", "Mumbai", "Pune"]:
    pred = coefs["Intercept"] + coefs["experience"] * years + coefs.get(city, 0.0)
    print(f"{city}: predicted log wage {pred:.3f}")

gap = coefs["Mumbai"] - coefs["Pune"]
print(f"Mumbai minus Pune: {gap:.2f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If `years = 0`, Delhi would print `Delhi: predicted log wage 10.200`.

## After you answer

- Why does Pune not need its own line in the dictionary to be compared with Mumbai? What does `coefs.get(city, 0.0)` do for Delhi?
