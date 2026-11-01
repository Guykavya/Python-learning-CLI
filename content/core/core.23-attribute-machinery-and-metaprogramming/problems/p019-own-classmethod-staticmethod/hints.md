## Hint 1

`Lab.from_fahrenheit` calls `ClassMethod.__get__(desc, None, Lab)`; `lab.from_fahrenheit`
calls `ClassMethod.__get__(desc, lab, Lab)`. In both cases, which argument holds the class
you want to bind to? Which standard-library type makes "a function with its first argument
already filled in" that has `__self__` and `__func__`?

## Hint 2

```
ClassMethod.__get__(instance, owner=None):
    if owner is None: owner = type(instance)
    return MethodType(self.__func__, owner)

StaticMethod.__get__(instance, owner=None):
    return self.__func__

StaticMethod.__call__(*args, **kwargs):
    return self.__func__(*args, **kwargs)
```
