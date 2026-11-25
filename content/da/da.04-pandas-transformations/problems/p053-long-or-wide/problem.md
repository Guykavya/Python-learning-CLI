# Long or wide?

Chapter sections 8.1 to 8.4. The same facts, revenue per store and quarter, can be kept in two shapes:

```text
long (tidy)                          wide
store_id  quarter  revenue           store_id   2024Q1   2024Q2
S1        2024Q1   299858            S1         299858   280256
S1        2024Q2   280256            S2         303269   346731
S2        2024Q1   303269
S2        2024Q2   346731
```

A teammate asks: "Which shape should we keep?" Explain in `answer.md`, in about 200 to 300 words:

1. What does **tidy** (long) mean, and why is it the better shape for analysis? Use `groupby` as your example.
2. When is **wide** the better shape? Give two concrete uses.
3. Which shape would you choose for each of these, and why: (a) a line chart of revenue over quarters, one line per
   store, with a plotting library; (b) a printed table for the monthly meeting; (c) storing the data in a file or a
   database table that grows every quarter; (d) "total revenue per quarter".
4. How do you move between the two shapes, and what do you check after moving?

## Example

A start: "In the long table every row is one fact: one store, one quarter, one revenue. Adding a new quarter adds
rows, not columns, so the code that reads the table does not change..."
