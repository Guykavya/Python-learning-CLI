# Product code validator

A product code looks like `AB-1234`: two capital letters (A to Z), a dash, four digits.

The first line is a number `N`. Then come `N` codes, one per line (strip spaces). For each
code print `<code>: valid` or `<code>: invalid (<reason>)`, where the reason is the **first**
problem found, checked in this order:

1. `length`: the code is not exactly 7 characters
2. `letters`: the first two characters are not both capital letters A to Z
3. `dash`: the third character is not `-`
4. `digits`: the last four characters are not all digits 0 to 9

Finally print `Valid: V of N`.

**Example**

Input:
```
3
AB-1234
ab-1234
AB1234
```
Output:
```
AB-1234: valid
ab-1234: invalid (letters)
AB1234: invalid (length)
Valid: 1 of 3
```
