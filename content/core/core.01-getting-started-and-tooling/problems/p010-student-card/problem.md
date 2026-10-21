# Student card

Read three lines from the keyboard: a **name**, a **course** and a **year**.
Print a card like this:

```
+--------------------+
Name   : Asha
Course : BCA
Year   : 1
+--------------------+
```

- The border is `+`, then exactly **20** `-` signs, then `+`.
- The labels are padded with spaces so the colons line up: `Name   :` has three
  spaces, `Course :` has one, `Year   :` has three. There is one space after
  each colon.
- Print the values exactly as typed.

Use `input()` with **no prompt message**. The checker types the input for you
and compares your printed lines exactly.

**Example**

Input:
```
Ravi Kumar
BCA
2
```
Output:
```
+--------------------+
Name   : Ravi Kumar
Course : BCA
Year   : 2
+--------------------+
```
