# Mutual friends and suggestions

Read two lines in the form `NAME: friend friend friend ...` (the friend list may be empty).
Print:

```
Mutual: <friends of both>
Suggest to <NAME1>: <friends of NAME2 who are not friends of NAME1, and not NAME1 itself>
Suggest to <NAME2>: <friends of NAME1 who are not friends of NAME2, and not NAME2 itself>
Network size: <number of distinct people: both names and all friends>
```

Names in each list are sorted alphabetically and separated by spaces. Print `none` for an
empty list. A friend list might repeat a name; count it once. Neither person lists themselves.

**Example**

Input:
```
asha: ravi meena kiran
ravi: asha kiran john
```
Output:
```
Mutual: kiran
Suggest to asha: john
Suggest to ravi: meena
Network size: 5
```

`ravi` is a friend of `asha`, so he is not suggested to her, and she is not suggested to herself.
