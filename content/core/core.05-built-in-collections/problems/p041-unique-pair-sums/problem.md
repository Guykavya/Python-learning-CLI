# Distinct pairs with a sum

Read a line of integers and then a target. Find every **distinct pair of values** `(a, b)`
with `a <= b` and `a + b == target`, using two different positions of the list. (So `5 + 5`
needs two 5s in the list.)

Print each pair as `a + b`, sorted by `a`, then `Pairs: <count>`.

**Example**

Input:
```
1 5 7 -1 5 3 3 9
6
```
Output:
```
-1 + 7
1 + 5
3 + 3
Pairs: 3
```

`1 + 5` is printed once, even though there are two 5s. The tests include 100,000 numbers.
