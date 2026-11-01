# Trace: start, run, join and Event

Threads usually run in an order you cannot predict. This program is different: every place
where the order matters is **forced** by `join()` (wait until that thread has finished) or by
an `Event` (`wait()` blocks until another thread calls `set()`). So its output is the same on
every run.

Remember:

- Creating a `Thread` does not run anything. `start()` asks the OS to run the target in a
  **new** thread and returns at once.
- `run()` is the method that `start()` calls inside the new thread. Calling `run()` yourself
  just calls the target **in the current thread**, like a normal function.
- `is_alive()` is `True` from `start()` until the target returns.
- `threading.current_thread().name` is the name of the thread executing that line. The main
  thread is called `MainThread`.

What does this program print?

```python
import threading


def greet(who):
    print(f"{who} runs in {threading.current_thread().name}")


a = threading.Thread(target=greet, args=("A",), name="worker-A")
print("created, alive:", a.is_alive())
a.start()
a.join()
print("A joined, alive:", a.is_alive())

b = threading.Thread(target=greet, args=("B",), name="worker-B")
b.run()
print("after b.run(), alive:", b.is_alive())

started = threading.Event()
go = threading.Event()


def slow():
    print("C: started")
    started.set()
    go.wait()
    print("C: finished")


c = threading.Thread(target=slow, name="worker-C")
c.start()
started.wait()
print("main: C alive?", c.is_alive())
print("main: keeps going while C waits")
go.set()
c.join()
print("main: C alive?", c.is_alive())

results = []
d = threading.Thread(target=lambda: results.append(sum(range(5))))
d.start()
d.join()
print("result from d:", results)
print("end of", threading.current_thread().name)
```

**Example**: the first line is `created, alive: False`. The thread object exists, but it has
not been started, so nothing is running yet.

Write in `answer.txt` the lines the program prints, in order.
