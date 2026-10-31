## Hint 1

You need two functions. The **global** tracer is called once per new frame: how can it tell if
the frame is running `fn`? What should it return for frames it is not interested in, and what
for the frames it is? The **local** tracer sees each `"line"` event; how do you turn
`frame.f_lineno` into a relative number?

## Hint 2

Keep the hits dictionary in the enclosing function so both tracers can reach it (closures).
The local tracer must return itself to keep receiving events.

```
code = fn.__code__
hits = {}
def local(frame, event, arg):
    if event == "line":
        rel = frame.f_lineno - code.co_firstlineno + 1
        hits[rel] = hits.get(rel, 0) + 1
    return local
def global_tracer(frame, event, arg):
    return local if frame.f_code is code else None
old = sys.gettrace()
sys.settrace(global_tracer)
try: fn(*args, **kwargs)
finally: sys.settrace(old)
return hits
```
