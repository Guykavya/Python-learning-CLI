## Hint 1

Separate two questions: "can two threads run **bytecode** at the same instant?" and "can a
thread be paused **between** two bytecodes of the same line?" Which one does the GIL answer?
What happens to the GIL while a thread is inside `time.sleep()` or `sock.recv()`?

## Hint 2

Write a two-thread timeline for `counter += 1`, starting with `counter = 10`:

```
thread A: LOAD counter (10)
          -- switch (5 ms interval) --
thread B: LOAD counter (10), ADD, STORE 11
          -- switch --
thread A: ADD, STORE 11      -> one increment lost
```

Then: in the free-threaded build both threads can be **between** LOAD and STORE at the same
moment. Better or worse?
