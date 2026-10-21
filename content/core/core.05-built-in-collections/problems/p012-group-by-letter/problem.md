# Group words by first letter

Read one line of words. Group them by their **first letter**, ignoring case (so `Apple` and
`avocado` share the group `a`). Print one line per group:

```
<letter>: <words in that group, separated by spaces>
```

Groups appear in the order their letter is **first seen**. Inside a group, words keep their
input order and their original spelling. If there are no words, print nothing.

**Example**

Input:
```
apple Banana avocado cherry bean Apricot
```
Output:
```
a: apple avocado Apricot
b: Banana bean
c: cherry
```
