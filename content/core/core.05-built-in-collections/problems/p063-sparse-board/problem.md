# A huge sparse board

A game board has `10**9` rows and `10**9` columns. Almost every cell is 0. A list of lists
would need 10^18 cells, which is impossible. Store only the non-zero cells.

Read commands until `end`:

| Command | Behaviour |
|---|---|
| `set R C V` | cell (R, C) becomes V (an integer; V may be 0, which clears the cell) |
| `get R C` | print the value of (R, C) |
| `row R` | print the sum of row R |
| `col C` | print the sum of column C |
| `count` | print how many cells are non-zero |

**Example**

Input:
```
set 5 7 10
set 5 900000000 -3
set 2 7 4
get 5 7
get 1 1
row 5
col 7
set 5 7 0
count
col 7
end
```
Output:
```
10
0
7
14
2
4
```

The tests run 100,000 commands, so `row` and `col` must not loop over every stored cell.
