## Hint 1

Keep two columns on paper: the run counter `n` and the namespace (`price`, `total`). Which cells change a variable and which only read one?

## Hint 2

Cell 3 changes `price` but nothing recomputes `total`. So when cell 2 or cell 4 prints `total` afterwards, which value of `price` was it computed from? Only a re-run of cell 1 brings them back in line.

## Hint 3

```text
run 1: cell 0   price=50
run 2: cell 1   total=150
run 3: cell 2   prints total 150
run 4: cell 3   price=80          (total still 150)
run 5: cell 4   prints price 80 total 150
...
```
Continue the sequence, then reset the counter to 0 after the restart.
