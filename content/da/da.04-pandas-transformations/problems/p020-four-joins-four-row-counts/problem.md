# Four joins, four row counts

Chapter sections 6.2 to 6.4. Before every merge, ask how many rows should come out; after it, check. The row count of
each join follows from three facts: which keys match, which side's unmatched rows are kept, and how many times each
key appears on each side.

Here `cust` has 5 customers. `orde` has 4 orders: customer `C1` ordered **twice**, `C9` does not exist in `cust`
(an orphan key), and `C2`, `C4`, `C5` never ordered.

```python
import pandas as pd

cust = pd.DataFrame({"customer_id": ["C1", "C2", "C3", "C4", "C5"],
                     "city": ["Pune", "Delhi", "Agra", "Surat", "Pune"]})
orde = pd.DataFrame({"order_id": [101, 102, 103, 104],
                     "customer_id": ["C1", "C3", "C1", "C9"],
                     "amount": [50, 20, 70, 10]})

for how in ["inner", "left", "right", "outer"]:
    r = cust.merge(orde, on="customer_id", how=how)
    print(how, len(r), r["customer_id"].tolist())

chk = cust.merge(orde, on="customer_id", how="outer", indicator=True)
counts = chk["_merge"].value_counts()
print(int(counts["both"]), int(counts["left_only"]), int(counts["right_only"]))

left = cust.merge(orde, on="customer_id", how="left")
print(int(left["order_id"].isna().sum()), str(left["order_id"].dtype))
print(int(left["amount"].sum()), int(orde["amount"].sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

Two facts about the **order of rows** (measured on pandas 3.1, Ch. 6.2): `inner` and `left` keep the order of the left
table's keys, `right` keeps the order of the right table, and `outer` sorts the keys.

## Example

With `a = pd.DataFrame({"k": ["x", "y"]})` and `b = pd.DataFrame({"k": ["x", "x", "z"]})`:
`len(a.merge(b, on="k", how="inner"))` is 2 (x matches twice), `how="left"` gives 3 (x twice, y once with missing
values), `how="right"` gives 3 and `how="outer"` gives 4.

## After you answer

- Which join "lost" an order, and which line of output shows the money that went missing with it?
- Why did `order_id` turn into `float64` in the left join?
