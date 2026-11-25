# Count people, not probabilities

Chapter section 10.3. Thinking in **counts of people** makes Bayes' theorem easy. The program splits 10,000 people into four groups (1% are sick, 99% of the sick test positive, 5% of the healthy test positive).

```python
people = 10_000
sick = people * 1 // 100
healthy = people - sick
sick_pos = sick * 99 // 100
sick_neg = sick - sick_pos
healthy_pos = healthy * 5 // 100
healthy_neg = healthy - healthy_pos
print(sick, healthy)
print(sick_pos, sick_neg)
print(healthy_pos, healthy_neg)
print(f"{sick_pos}/{sick_pos + healthy_pos}")
print(f"{sick_pos / (sick_pos + healthy_pos):.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For 1,000 people with the same rates, the first line would be `10 990`.

## After you answer

- Among the positives, how many are sick and how many are healthy? What does that say about "99% accurate"?
