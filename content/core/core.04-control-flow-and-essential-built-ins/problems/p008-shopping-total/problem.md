# Shopping total with a sentinel

Read item prices, one per line, until a line that says `done`. The word may have any
capitals and spaces around it, like `  DONE `. Prices may have decimals.

Print:

```
Items: <how many prices>
Total: <sum, with 2 decimals>
```

**Example**

Input:
```
12.50
3
40.25
done
```
Output:
```
Items: 3
Total: 55.75
```

If `done` is the very first line, print `Items: 0` and `Total: 0.00`.
