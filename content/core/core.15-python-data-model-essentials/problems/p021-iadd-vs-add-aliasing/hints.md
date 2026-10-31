## Hint 1

Draw it: one box per object, arrows for names. After `b = a` both names have an arrow to the same box. Then ask for each `+` or `+=`: is the box changed, or is a new box built and only the left name moved?

## Hint 2

```
a = a + Bag([2])   -> new Bag; a moves; b still points to the old Bag
a += Bag([2])      -> __iadd__ changes the Bag and returns self; a is b
Plain has no __iadd__ -> p += q becomes p = p + q -> new object
Buggy.__iadd__ returns None -> after `x += ...`, x IS None
```
