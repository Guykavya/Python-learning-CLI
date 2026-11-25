## Hint 1

`pd.cut(x, bins=edges, labels=...)` uses the edges you give, `pd.qcut(x, q=4, labels=...)` computes the edges from the data (section 15.4). Which bins are open and which closed by default? What does `right=True` imply for a value that equals an edge, and what happens to the very first edge (0 here)?

## Hint 2

```text
age_bands:      pd.cut(s, bins=[0, 18, 40, 65, np.inf],
                       labels=["youth", "adult", "middle", "senior"],
                       include_lowest=True)          # so that 0 is not left out
spend_quartiles: pd.qcut(s, q=4, labels=["Q1", "Q2", "Q3", "Q4"])
```
Both are right-closed by default, which is what the statement asks for. `inf` as the last edge makes the last band open-ended.
