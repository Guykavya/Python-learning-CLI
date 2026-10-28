## Hint 1

For each `+` write the two types, then apply the rules in order. In `A() + B()` where `B` is a subclass of `A`, check whether `B` overrides `__radd__` (it does) before trying `A.__add__`.

## Hint 2

```
A() + A()    -> A.__add__ answers
A() + B()    -> B is a subclass of A and overrides __radd__ -> B.__radd__ FIRST
B() + A()    -> A is not a subclass of B -> B.__add__ (inherited from A)
D() + C()    -> D.__add__ declines -> C.__radd__
1 + A()      -> int declines -> A.__radd__
D() + 1      -> D.__add__ declines, int has no __radd__ answer -> TypeError
```
