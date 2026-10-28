## Hint 1

A protocol is an ordinary-looking class that lists the methods a type must have. What do you put in the body of a method that is only a description? And what must the class inherit from to become a protocol?

## Hint 2

`class Closeable(Protocol):` with one method, `def close(self) -> None: ...` (the three dots are the body). The two functions are plain code: loop and call `close()`. Which statement lets you swallow an error and return `False`? Catch `Exception`, not everything: why?

## Hint 3

```
class Closeable(Protocol):
    def close(self) -> None: ...

def close_all(items):
    n = 0
    for item in items:
        item.close()
        n += 1
    return n

def close_quietly(item):
    try: item.close()
    except Exception: return False
    return True
```
