## Hint 1

For each `compile` call, first ask: which mode, and what does running a code object of that
mode *return*? Then ask what is printed by the call itself (only `"single"` mode prints on its
own). What does `exec` add to a namespace dict that had no `__builtins__`?

## Hint 2

Go block by block:

```
eval-mode code    -> eval returns the value         (x * 2 with 21, then with "ab")
exec              -> always returns None
exec-mode "x * 2" -> the expression is evaluated and thrown away, so eval(...) gives None
eval mode + statement -> compile itself raises (which exception? what is e.filename?)
single mode       -> exec prints the value of the expression, then returns None
```
