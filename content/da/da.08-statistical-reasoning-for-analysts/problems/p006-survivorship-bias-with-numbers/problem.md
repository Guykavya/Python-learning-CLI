# Survivorship bias with numbers

Chapter section 3. A report on "how the shops of a mall grew over two years" uses only the shops that are still open. Each tuple is
`(shop, still_open, growth_percent)`; for a closed shop the growth is what it achieved until it closed.

```python
shops = [
    ("A", True, 12), ("B", True, 8), ("C", False, -5), ("D", True, 15), ("E", False, -20),
    ("F", True, 10), ("G", False, -15), ("H", True, 6), ("I", False, -30), ("J", True, 9),
]

open_growth = [g for _, still_open, g in shops if still_open]
all_growth = [g for _, _, g in shops]

print("closed:", len(shops) - len(open_growth), "of", len(shops))
print(f"survivors: {sum(open_growth) / len(open_growth):.1f}")
print(f"all shops: {sum(all_growth) / len(all_growth):.1f}")
print(f"gap: {sum(open_growth) / len(open_growth) - sum(all_growth) / len(all_growth):.1f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `[("A", True, 10), ("B", False, -10)]` the survivors' mean is 10.0 and the mean of all is 0.0, a gap of 10.0.

## After you answer

- Which group does the report that uses survivors only describe, and who is missing from it?
- Name another place where a "winners only" average hides the losers.
