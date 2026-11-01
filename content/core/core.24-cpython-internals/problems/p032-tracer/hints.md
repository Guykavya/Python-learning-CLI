## Hint 1

You need **two** functions: one that receives `"call"` events and decides whether a frame is
interesting, and one that receives the `"line"` events of the frames you said yes to. What does
the global one return for a frame from another file? What must the local one return so that it
keeps getting events?

Where do the function name and the line number come from? (Look at `frame.f_code` and
`frame.f_lineno`.) How do you guarantee that the old tracer is put back if `func` raises?

## Hint 2

```
trace_lines(func, *args, **kwargs):
    filename = func.__code__.co_filename
    events = []

    local(frame, event, arg):
        if event == "line":
            events.append((frame.f_code.co_name, frame.f_lineno - frame.f_code.co_firstlineno))
        return local

    global_(frame, event, arg):          # event is "call"
        return local if frame.f_code.co_filename == filename else None

    previous = sys.gettrace()
    sys.settrace(global_)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(previous)
    return result, events

line_counts(events, name): Counter(line for n, line in events if n == name)
```
