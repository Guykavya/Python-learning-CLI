# Sales by city

Read `n`, then `n` sales lines of `city item quantity`. Build a dict of dicts:
`sales[city][item]` is the total quantity of that item sold in that city.

Print each city in alphabetical order with its total, and under it each item (alphabetical)
indented by two spaces:

```
<city>: <city total>
  <item> <quantity>
```

**Example**

Input:
```
5
pune tea 3
delhi rice 10
pune rice 2
pune tea 4
delhi dal 1
```
Output:
```
delhi: 11
  dal 1
  rice 10
pune: 9
  rice 2
  tea 7
```
