## Hint 1

Picture the lookup as two doors. Which hook is the door every read passes through, and which one
is only opened after the first door said "not found"? For the proxy, do you want the hook to run
when the proxy reads its own `self._target`?

## Hint 2

Shape of a good answer:

```
1. getattribute: every read; default = normal lookup
   getattr: only when the normal lookup raised AttributeError
2. (a) getattr  (b) getattr  (c) getattribute  -- one reason each
3. recursion (self.x inside it) + slow/global; fix: super().__getattribute__(name)
4. raise AttributeError(name); hasattr/getattr default/copy/pickle depend on it
```
