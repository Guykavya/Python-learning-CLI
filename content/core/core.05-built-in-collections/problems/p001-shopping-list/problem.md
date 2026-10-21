# Shopping list builder

Read item names, one per line, until a line that says `done`. Store them in a list
with `append`. Then print how many items there are, followed by a numbered list.

```
Items: <count>
1. <first item>
2. <second item>
...
```

If there are no items, print `Items: 0` and then `The list is empty.`

Duplicates are allowed: if `milk` is typed twice, it appears twice.

Use `input()` without a prompt.

**Example**

Input:
```
rice
milk
dal
milk
done
```
Output:
```
Items: 4
1. rice
2. milk
3. dal
4. milk
```
