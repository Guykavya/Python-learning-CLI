# Unique visitors in order

A website logs visitor names. Read `n`, then `n` names, one per line. Print how many
**distinct** visitors there were, then each distinct name once, in the order of their **first**
visit:

```
Unique: <count>
<name>
<name>
...
```

**Example**

Input:
```
6
ravi
asha
ravi
meena
asha
ravi
```
Output:
```
Unique: 3
ravi
asha
meena
```

The tests include 100,000 visits. Checking `if name not in some_list` for each visit is far too
slow at that size. Use a set to remember who you have seen.
