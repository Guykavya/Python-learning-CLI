## Hint 1

Which lines must run **without another thread getting in between**? If thread A has read
`_value` but not yet written it back, what must thread B be prevented from doing? Where should
the lock be created so that every thread uses the **same** lock for the same counter?

## Hint 2

```
__init__:
    self._value = 0
    self._lock = threading.Lock()

increment:
    with self._lock:          # only one thread at a time past this line
        current = self._value
        time.sleep(0)
        self._value = current + 1
```

`with` releases the lock even if something inside raises. Does `value` need the lock too?
