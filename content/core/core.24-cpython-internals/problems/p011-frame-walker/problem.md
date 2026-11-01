# Walk the call stack

Each running function call has a **frame** object: its local variables, the line it is on, the
code object it runs (`frame.f_code`) and a link to the frame of its caller (`frame.f_back`). The
frames form a chain that ends at the module's frame, whose code object is named `"<module>"`.
A traceback is just this chain, printed.

`sys._getframe(0)` returns the current frame, `sys._getframe(1)` the caller's frame, and so on.
(The leading underscore means "CPython-specific"; `inspect.currentframe()` is the portable
spelling of `sys._getframe(0)`.)

Copy `starter.py` to `solution.py` and write **`call_chain(stop=None, qualified=False)`**. It
returns a list of function names, starting with the function that **called** `call_chain`
(not `call_chain` itself) and going outwards through the callers.

- Stop **before** the first frame whose code object is named `"<module>"`, or before the first
  frame whose name equals `stop` (when `stop` is given). That frame is not included.
- If no such frame is found, return every name up to the end of the chain.
- Use `co_name` by default. With `qualified=True` use `co_qualname` (3.11+), the dotted name that
  includes the class or enclosing function, like `"Greeter.hello"` or `"outer.<locals>.inner"`.

**Example**

```python
def outer():
    return middle()

def middle():
    return inner()

def inner():
    return call_chain()

outer()        # ['inner', 'middle', 'outer']   (when outer() is called from module level)
```

Do not keep frame objects around after you are done with them: a frame holds all its local
variables alive.
