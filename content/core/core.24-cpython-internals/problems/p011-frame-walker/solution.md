## Approach

Frames form a singly linked list through `f_back`, from the innermost call outwards. Walk it
like any linked list, read the name from each frame's code object, and stop at the first frame
that is a module or the requested `stop`. Starting at `sys._getframe(1)` leaves out
`call_chain` itself.

## Code

```python
import sys


def call_chain(stop=None, qualified=False):
    frame = sys._getframe(1)
    names = []
    while frame is not None:
        code = frame.f_code
        if code.co_name == "<module>" or code.co_name == stop:
            break
        names.append(code.co_qualname if qualified else code.co_name)
        frame = frame.f_back
    del frame
    return names
```

## Complexity

O(d) where d is the depth of the call stack.

## Another way

`inspect.stack()` returns a list of `FrameInfo` records (innermost first) with a `.function`
attribute. It is portable but much slower, because it also reads source lines for every frame:

```python
import inspect

def call_chain(stop=None, qualified=False):
    names = []
    for info in inspect.stack()[1:]:
        code = info.frame.f_code
        if code.co_name in ("<module>", stop):
            break
        names.append(code.co_qualname if qualified else code.co_name)
    return names
```

(Comparing with `in ("<module>", stop)` works because `stop=None` never equals a name.)

**Version note.** In 3.11 a list comprehension runs in its own frame named `<listcomp>`; since
3.12 it is inlined into the function (PEP 709) and has no frame. Call chains that pass through a
comprehension therefore differ between versions, which is why the tests do not use one.
