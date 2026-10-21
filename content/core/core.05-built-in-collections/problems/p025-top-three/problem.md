# Top three scores

Read `n`, then `n` lines of `name score` (integer scores, names are unique). Print the top
three (or fewer, if there are fewer than three people):

```
1. <name> <score>
2. <name> <score>
3. <name> <score>
```

Higher scores come first. When scores tie, names are in **alphabetical** order. If `n` is 0,
print `No scores.`

You do not need `lambda`: sort **tuples** whose first item makes the order you want.

**Example**

Input:
```
5
ravi 70
asha 90
meena 85
john 90
zoe 85
```
Output:
```
1. asha 90
2. john 90
3. meena 85
```
