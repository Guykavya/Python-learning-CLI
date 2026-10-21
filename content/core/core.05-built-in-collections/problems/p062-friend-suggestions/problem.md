# Friend suggestions

Read `n`, then `n` friendship lines `A B` (friendship goes both ways; repeated lines are
harmless). Then read `q` and `q` names.

For each name, suggest up to three new friends: people who are friends of the person's friends,
but are not the person and not already a friend. Rank them by the number of **mutual friends**
(highest first), then by name. Print:

```
NAME: s1 (m1), s2 (m2), s3 (m3)
```

or `NAME: no suggestions`. A name that appears in no friendship has no suggestions.

**Example**

Input:
```
5
asha ravi
asha meena
ravi john
meena john
ravi kiran
2
asha
kiran
```
Output:
```
asha: john (2), kiran (1)
kiran: asha (1), john (1)
```

`john` is a friend of both `ravi` and `meena`, so he has 2 mutual friends with `asha`.
