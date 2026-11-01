## Hint 1

`sys._getframe(1)` already skips `call_chain`'s own frame. From any frame, which attribute takes
you one step out, and what is it when there are no more callers? Where is the function name
kept: on the frame, or on its code object?

## Hint 2

```
frame = sys._getframe(1)
names = []
while frame is not None:
    code = frame.f_code
    if code.co_name == "<module>" or code.co_name == stop: break
    names.append(code.co_qualname if qualified else code.co_name)
    frame = frame.f_back
return names
```
