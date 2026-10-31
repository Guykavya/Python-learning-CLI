## Hint 1

Try it: add `print(self)` and `print(c)` in a working version of the class. Are they the same
object? Then call `Counter.tick(c)` directly. Does it do the same as `c.tick()`?

## Hint 2

Structure your answer around the five points:

```
1. self = the object before the dot
2. c.tick()  ==  Counter.tick(c)  -> one hidden argument -> "1 was given"
3. count = 0 is a local variable -> AttributeError later -> self.count = 0
4. reasons: attribute vs local is visible; assignment rule; methods are plain functions
   (Cls.method(obj), super()); "explicit is better than implicit"
5. only a convention, but always use it
```
