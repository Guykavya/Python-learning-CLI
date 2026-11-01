## Hint 1

When you print `compile(NESTED, "<src>", "exec").co_consts`, what kind of object stands for the
nested `def`? How can you recognise it, and what do you do with it? For `is_folded`, why is
`value in constants` not enough when `value` is `1000` and the constant is `1000.0`?

## Hint 2

```
CodeType = type(compile("", "<src>", "exec"))

all_constants(source, mode):
    found = [], todo = [compile(source, "<src>", mode)]
    while todo:
        code = todo.pop()
        for const in code.co_consts:
            if const is a CodeType: todo.append(const)
            else: found.append(const)
    return found

is_folded(expr, value):
    any const in all_constants(expr, "eval") with type(const) is type(value) and const == value
```
