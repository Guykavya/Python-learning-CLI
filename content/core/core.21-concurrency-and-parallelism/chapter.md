# Chapter 21: Concurrency and parallelism

Most programs you have written so far do one thing at a time. Line 1 runs, then line 2, then line 3. That is simple and easy to reason about, and for most scripts it is exactly right.

But think about what real programs spend their time on. A web scraper sends a request and then **waits** half a second for the server to answer. A chat server **waits** for any of a thousand users to type something. A photo app **computes** for two seconds per image while seven of your eight CPU cores sit idle. In the first two cases the program is not slow because Python is slow; it is slow because it waits, one thing after another, when it could be waiting for many things at once. In the third case the computer has more power than the program is using.

This chapter teaches you how to do several things at once in Python, safely. You will learn three tools, and more importantly, **which one to pick and why**: **threads** (`threading`, `ThreadPoolExecutor`) for programs that wait a lot; **processes** (`multiprocessing`, `ProcessPoolExecutor`) for programs that compute a lot; and **asyncio** (`async`/`await`) for programs that wait for *very many* things, such as thousands of network connections. Along the way you will meet the problems that concurrency brings with it (race conditions, deadlocks, lost errors, programs that never stop) and the standard tools that solve them: locks, events, semaphores, queues, futures, task groups, timeouts and cancellation. The chapter ends with `httpx`, a real async HTTP library, and a design walkthrough of the module project: a concurrent downloader with limits, retries, timeouts and safe files.

The chapter has three learning outcomes:

1. **Choose the right model**: tell I/O-bound work from CPU-bound work, and pick threads, processes or asyncio for a given problem, with reasons.
2. **Write correct concurrent code**: protect shared data with locks, avoid deadlocks, pass work through queues, and collect results and errors from many workers.
3. **Write robust async code**: run tasks concurrently, limit how many run at once, add timeouts, cancel cleanly without leaking resources, and talk to HTTP servers with `httpx`.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux (8 CPU cores, normal GIL build). File paths are shown as `/home/you/conc/...`. **Timings are machine-specific: your times will differ.** What should match is the *shape*: "4 downloads took about as long as 1" or "threads were no faster than a plain loop". **Thread idents, process ids and memory addresses are machine-specific too**; they change on every run. Where the order of output depends on timing, the text says so, and the demo is built so the shown order is the one you will normally see. Some examples show only the key lines of a program (an excerpt, often reusing a function from just before); their output comes from running the full program. Everything up to section 15 uses only the standard library. Section 16 and the project use `httpx` (installed with this course). No example touches the real network: every HTTP example uses `httpx.MockTransport`, a fake server inside your program.

## Table of contents

[1. Why concurrency](#1-why-concurrency) · [2. Processes and threads](#2-processes-and-threads) · [3. `threading` basics](#3-threading-basics) · [4. The GIL and free-threaded Python](#4-the-gil-and-free-threaded-python) · [5. Race conditions, `Lock` and `RLock`](#5-race-conditions-lock-and-rlock) · [6. Deadlocks](#6-deadlocks) · [7. Coordinating threads: events, semaphores, conditions, queues](#7-coordinating-threads-events-semaphores-conditions-queues) · [8. `multiprocessing`](#8-multiprocessing) · [9. `concurrent.futures`](#9-concurrentfutures) · [10. asyncio basics](#10-asyncio-basics) · [11. Tasks, `gather` and `TaskGroup`](#11-tasks-gather-and-taskgroup) · [12. Timeouts and cancellation](#12-timeouts-and-cancellation) · [13. Bounded concurrency and shared state in asyncio](#13-bounded-concurrency-and-shared-state-in-asyncio) · [14. Blocking calls inside async code](#14-blocking-calls-inside-async-code) · [15. Async iterators, generators and context managers](#15-async-iterators-generators-and-context-managers) · [16. `httpx` for async HTTP](#16-httpx-for-async-http) · [17. Choosing the right tool](#17-choosing-the-right-tool) · [18. Module project: a concurrent downloader](#18-module-project-a-concurrent-downloader) · [19. Common traps](#19-common-traps) · [20. Summary](#20-summary)

## 1. Why concurrency

### 1.1 Waiting versus computing

Every slow program is slow for one of two reasons:

- It is **waiting** for something outside the CPU: a network reply, a disk, a database, a user, a timer. During the wait the CPU has nothing to do. This kind of work is called **I/O-bound** (I/O = input/output).
- It is **computing**: multiplying matrices, resizing images, searching through numbers. The CPU is 100% busy the whole time. This kind of work is called **CPU-bound**.

Here is an I/O-bound program. `time.sleep(0.5)` stands in for "waiting half a second for a server":

```python
import time

def download(name):
    time.sleep(0.5)          # pretend: waiting for the network
    return f"{name}: done"

start = time.perf_counter()
for name in ["a.html", "b.html", "c.html", "d.html"]:
    print(download(name))
print(f"took {time.perf_counter() - start:.2f} s")
```
```text
a.html: done
b.html: done
c.html: done
d.html: done
took 2.00 s
```

Two seconds, and the CPU did almost nothing. The four downloads do not depend on each other; there is no reason to wait for `a.html` to arrive before *asking* for `b.html`. Now replace the loop with a pool of 4 threads, timed the same way (sections 3 and 9 explain how this works):

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as pool:
    for line in pool.map(download, ["a.html", "b.html", "c.html", "d.html"]):
        print(line)
```

It printed the same four lines, then `took 0.50 s` (your times will differ a little). Four waits **overlapped**, so the whole job took as long as one wait. That is the whole promise of concurrency for I/O-bound work.

### 1.2 The same trick fails for computing

Now a CPU-bound job: counting prime numbers below 200,000, four times.

```python
import time
from concurrent.futures import ThreadPoolExecutor

def count_primes(limit):
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count

jobs = [200_000] * 4

start = time.perf_counter()
print([count_primes(n) for n in jobs])
print(f"serial:  {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    print(list(pool.map(count_primes, jobs)))
print(f"threads: {time.perf_counter() - start:.2f} s")
```
```text
[17984, 17984, 17984, 17984]
serial:  2.57 s
[17984, 17984, 17984, 17984]
threads: 2.87 s
```

The threads were **no faster**. In normal Python only one thread runs Python code at any moment (section 4 explains why: the GIL). Threads are great at *waiting together*, but they cannot *compute together*.

To compute in parallel, use several **processes**. Each process is a separate Python interpreter, with its own GIL, on its own CPU core. Swap the executor class and add the guard that processes need (section 8), timed the same way:

```python
from concurrent.futures import ProcessPoolExecutor

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as pool:
        print(list(pool.map(count_primes, jobs)))
```
```text
[17984, 17984, 17984, 17984]
processes: 1.23 s
```

About twice as fast (your times will differ). Not four times: starting processes and sending data to them costs time, and four cores rarely give a perfect 4x.

### 1.3 Concurrency versus parallelism

These two words are often mixed up. They mean different things:

- **Concurrency** is about *structure*: several tasks are **in progress** at the same time. They may take turns on a single CPU. A cook who puts rice on the stove, then chops vegetables while the rice boils, is working concurrently. One person, several jobs in progress.
- **Parallelism** is about *execution*: several tasks are **running at the same instant**, on different CPU cores. Two cooks chopping vegetables side by side are working in parallel.

```text
Concurrency: one core, taking turns     Parallelism: several cores at once
  task A  ███░░░░░░███░░░░░░███            core 1  task A ████████████
  task B  ░░░███░░░░░░███░░░░░░            core 2  task B ████████████
  task C  ░░░░░░███░░░░░░███░░░            core 3  task C ████████████
```

Threads in normal Python and asyncio give you **concurrency**. Processes give you **parallelism**. For I/O-bound work concurrency is enough, because the "work" is mostly waiting, and waiting does not need a CPU. For CPU-bound work you need parallelism.

### 1.4 Measure first

Concurrency makes code harder to write, test and debug. Before you add it, **measure** (chapter 20): is the program really waiting, or really computing? A quick check:

- Run it and watch a system monitor (`htop`, Task Manager). One core at 100%? CPU-bound. All cores near 0% while it "works"? I/O-bound.
- Profile it with `cProfile`. If most time is in `socket.recv`, `time.sleep`, `select` or database calls, it is I/O-bound.
- Compare `time.process_time()` (CPU time used) with `time.perf_counter()` (wall-clock time). If CPU time is much smaller than wall time, the program is mostly waiting.

And ask whether you need concurrency at all. A program that runs once a night for 4 minutes may not be worth the complexity. A faster algorithm (chapter 20) often beats eight cores.

#### Try it 1.1

For each job, say whether it is mostly I/O-bound or CPU-bound.

1. Downloading 300 product pages from a shop website.
2. Turning 2,000 photos into small thumbnails.
3. A bot that answers Telegram messages.
4. Calculating SHA-256 checksums of 50 large files that are already in memory.
5. Copying 10,000 small files from a USB stick.

<details><summary>Answer</summary>

1. I/O-bound: almost all time is waiting for the server.
2. CPU-bound: decoding, resizing and encoding pixels is pure computation.
3. I/O-bound: the bot waits for messages and for the Telegram API.
4. CPU-bound: hashing is computation. (If the files first had to be read from a slow disk, the reading part would be I/O-bound.)
5. I/O-bound: the disk and the USB bus are the limit.

</details>

## 2. Processes and threads

### 2.1 What the operating system gives you

When you run `python script.py`, the operating system creates a **process**. A process is a running program with its own **memory** (all your variables and objects; no other process can see it), its own **open files and network connections**, and a **process id** (`pid`), a number that names it.

Inside every process there is at least one **thread**. A thread is a single line of execution: "which instruction am I running now, and what is on my call stack". A process starts with one thread, the **main thread**, and can create more. All threads in a process **share the same memory**: they see the same global variables and the same objects.

```text
  Process (pid 4021)                      Process (pid 4022)
  +----------------------------------+    +------------------------+
  |  memory: globals, objects, heap  |    |  memory: its OWN copy  |
  |                                  |    |                        |
  |  main thread   thread 2  thread 3|    |  main thread           |
  |  (own stack)   (stack)   (stack) |    |                        |
  +----------------------------------+    +------------------------+
         threads share memory                  processes do not
```

The **OS scheduler** decides which thread runs on which CPU core and for how long. It can pause a thread at almost any moment (after any machine instruction) and run another one. You do not control it, and you cannot predict it. That is the root of every problem in sections 5 and 6.

### 2.2 Seeing the difference

This program adds an item to a global list, once from a thread and once from a child process:

```python
import os
import threading
import multiprocessing

shopping = []

def add_item(item):
    shopping.append(item)
    print(f"  in worker: pid={os.getpid()} list={shopping}")

if __name__ == "__main__":
    print(f"main: pid={os.getpid()}")

    t = threading.Thread(target=add_item, args=("milk",))
    t.start()
    t.join()
    print(f"after thread:  {shopping}")

    p = multiprocessing.Process(target=add_item, args=("eggs",))
    p.start()
    p.join()
    print(f"after process: {shopping}")
```
```text
main: pid=11485
  in worker: pid=11485 list=['milk']
after thread:  ['milk']
  in worker: pid=11490 list=['eggs']
after process: ['milk']
```

(The pids are machine-specific.) Read it carefully:

- The thread ran in the **same process** (same pid) and changed the **same list**. The main thread sees `'milk'` afterwards.
- The child process has a **different pid** and its own copy of memory. It appended `'eggs'` to *its* list. The parent's list never changed. Notice also that the child's list did not contain `'milk'`: the child started fresh by re-importing the file (section 8.3), so its `shopping` began empty.

This is the most important fact about the two: **threads share memory, processes do not.** Sharing makes threads easy to use (just read the variable) and dangerous (two threads can change the same variable at the same time). Not sharing makes processes safe from each other, but every piece of data has to be **copied** between them.

### 2.3 What they cost

Creating a thread is cheap. Creating a process means starting a new Python interpreter. Timing 20 thread starts and 4 process starts, each running an empty function, `start()` then `join()`:

```text
one thread:  0.351 ms
one process: 41.2 ms
```

(Your times will differ; on Windows and macOS processes are usually slower still.) A process costs roughly a hundred times more to start and uses many megabytes of memory. So you start a few processes and give each a lot of work, but you can start hundreds of threads, and asyncio can juggle tens of thousands of tasks.

| | Thread | Process | asyncio task |
|---|---|---|---|
| Memory | shared with other threads | separate | shared (one thread) |
| Start-up cost | small (~0.1–1 ms) | large (~20–100 ms) | tiny (microseconds) |
| Runs Python in parallel? | no (normal GIL build) | yes | no |
| Who switches between them | the OS, at any moment | the OS | **you**, only at `await` |
| Typical count | tens to a few hundred | about one per CPU core | thousands |
| Good for | waiting (I/O) | computing (CPU) | very many waits (network) |

#### Try it 2.1

A program starts 3 threads and 2 processes. Each worker appends its name to a global list `names`, which starts empty in the parent. After all of them have been joined, how many items does the parent's `names` list contain?

<details><summary>Answer</summary>

**3.** The three threads share the parent's memory, so their appends land in the parent's list. The two processes append to their own copies, which are thrown away when they exit. To get data back from a process you must send it back on purpose: a return value through a pool (section 8.5), a `Queue`, or shared memory (section 8.6).

</details>

## 3. `threading` basics

### 3.1 Creating, starting and joining

A `threading.Thread` object describes a function to run in a new thread. Nothing runs until you call `start()`. `join()` waits until that thread has finished.

```python
import threading
import time

def greet(name, delay):
    time.sleep(delay)
    print(f"hello, {name}")

t1 = threading.Thread(target=greet, args=("Asha", 0.2))
t2 = threading.Thread(target=greet, args=("Ravi", 0.1))

t1.start()
t2.start()
print("both started")

t1.join()
t2.join()
print("both finished")
```
```text
both started
hello, Ravi
hello, Asha
both finished
```

Four things to notice:

1. **`target` is the function itself, not a call.** Write `target=greet`, not `target=greet("Asha", 0.2)`. The second form calls `greet` *now*, in the main thread, and passes its return value (`None`) as the target.
2. **`args` is a tuple.** For one argument write `args=("Asha",)` with the comma; `args=("Asha")` is just a string, and Python would try to pass its letters as separate arguments. `kwargs={"delay": 0.2}` passes keyword arguments.
3. **`start()` returns at once.** The main thread kept going and printed "both started" while the other two slept. Ravi printed first because his sleep was shorter, not because of the start order.
4. **`join()` blocks the caller** until the thread ends. Without the joins, "both finished" would print immediately.

The pattern **"start all, then join all"** is the one to remember. If you write `t1.start(); t1.join(); t2.start(); t2.join()` the threads run one after the other, and you gained nothing.

### 3.2 `start()` versus `run()`, and the end of the program

`Thread` has a method called `run()`. It is what `start()` calls *inside the new thread*. If you call `run()` yourself, it is an ordinary function call in the current thread:

```python
import threading

def show():
    print("running in:", threading.current_thread().name)

t = threading.Thread(target=show, name="worker-1")
t.run()      # WRONG: just a normal call
t = threading.Thread(target=show, name="worker-2")
t.start()    # RIGHT: a new thread
t.join()
```
```text
running in: MainThread
running in: worker-2
```

This mistake does not crash; the program just runs serially. (Giving threads a `name` makes logs readable. Each thread also has an `ident` and a `native_id`, numbers that are machine-specific and change every run; `threading.active_count()` and `threading.enumerate()` list the live threads, handy when you hunt a thread that never stopped.)

What if the main thread reaches the end of the file while another thread still runs? Python does **not** exit while ordinary threads are running: it quietly joins them first, so their work is not lost.

### 3.3 Daemon threads

Sometimes a thread runs forever on purpose: a heartbeat, a background cache cleaner. You do not want it to keep the program alive. Mark it as a **daemon** thread:

```python
import threading
import time

def heartbeat():
    while True:
        print("tick")
        time.sleep(0.1)

t = threading.Thread(target=heartbeat, daemon=True)
t.start()
time.sleep(0.25)
print("main done; the daemon thread is killed now")
```
```text
tick
tick
tick
main done; the daemon thread is killed now
```

When only daemon threads are left, Python exits and stops them **abruptly**: their `finally` blocks do not run, and files they were writing may be half-written. Rule: **daemon threads must never hold work that matters.** For a clean stop, use an `Event` (section 7.1) and join the thread.

### 3.4 Getting results back

`Thread` has no return value. If the target function returns something, it is thrown away. The simplest way to get results is to give each thread a place to put them:

```python
import threading
import time

def square_slowly(n, results, index):
    time.sleep(0.1 * (4 - n))      # bigger n finishes sooner
    results[index] = n * n

numbers = [1, 2, 3]
results = [None] * len(numbers)
threads = [
    threading.Thread(target=square_slowly, args=(n, results, i))
    for i, n in enumerate(numbers)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(results)
```
```text
[1, 4, 9]
```

Each thread writes to **its own slot**, so there is no conflict, and the results come out in **input order** even though the threads finished in reverse order. Writing to separate list slots is safe; section 5 shows what goes wrong when threads write to the *same* place. (You can also subclass `Thread`, override `run()` and store the result on `self`, but in real code you will usually use `ThreadPoolExecutor`, section 9, which returns results and errors for you.)

### 3.5 Exceptions inside threads

What happens when a thread raises an exception?

```python
import threading

def risky():
    raise ValueError("bad data in row 7")

t = threading.Thread(target=risky, name="loader")
t.start()
t.join()
print("main: join() returned normally, is_alive =", t.is_alive())
```
```text
Exception in thread loader:
Traceback (most recent call last):
  ... (two frames inside threading.py) ...
  File "/home/you/conc/thread_error.py", line 4, in risky
    raise ValueError("bad data in row 7")
ValueError: bad data in row 7
main: join() returned normally, is_alive = False
```

The traceback is **printed**, the thread dies, and that is all. The exception does **not** travel to the thread that called `join()`. The main thread carries on as if nothing happened. In a program that writes to a log file instead of a terminal, nobody may ever see that message.

This is a big difference from normal function calls, and a common source of "silent" bugs. You have three options:

1. **Catch inside the thread** and store the error like a result, for example `results[i] = ("error", e)` in an `except Exception as e:` block of the target.
2. **Use `ThreadPoolExecutor`** (section 9): its futures keep the exception and re-raise it when you ask for the result. This is the best default.
3. **Install `threading.excepthook`**, a function Python calls for every exception that escapes a thread. It receives one argument with the attributes `exc_type`, `exc_value`, `exc_traceback` and `thread`:

```python
errors = []

def remember(args):
    errors.append((args.thread.name, args.exc_type.__name__, str(args.exc_value)))

threading.excepthook = remember
```

With this hook installed, four threads named `t0`…`t3`, where only `t2` raises `ValueError("bad item 2")`, leave `errors == [('t2', 'ValueError', 'bad item 2')]` and print no traceback. Replacing the hook changes behaviour for the whole program, so in real code you usually log inside it rather than collect into a list.

#### Try it 3.1 (Predict the output)

```python
import threading
import time

log = []

def job(name, delay):
    time.sleep(delay)
    log.append(name)

a = threading.Thread(target=job, args=("A", 0.2))
b = threading.Thread(target=job, args=("B", 0.1))
a.start()
a.join()
b.start()
log.append("main")
b.join()
print(log)
```

<details><summary>Answer</summary>

```text
['A', 'main', 'B']
```

`a.join()` comes *before* `b.start()`, so A must finish first. Then B starts and sleeps 0.1 s, while the main thread appends `"main"` immediately. B appends last. Starting and joining one thread before starting the next makes the threads run one after another.

</details>

#### Try it 3.2

`run_task(f)` starts `threading.Thread(target=f)`, joins it, and returns. `f` raises `KeyError`. Does `run_task` raise? What does the user see? Name two ways to get the error back to the caller.

<details><summary>Answer</summary>

`run_task` does **not** raise. The thread prints `Exception in thread ...` and a traceback to stderr and dies; `join()` returns normally. Ways to get the error back: catch it inside the thread's target and store it (for example as `("error", exc)` in a results list), or run `f` through a `ThreadPoolExecutor` and call `future.result()`, which re-raises it. (`threading.excepthook` can also record it.)

</details>

## 4. The GIL and free-threaded Python

### 4.1 What the GIL is

CPython, the standard Python interpreter, has a **Global Interpreter Lock** (GIL). It is a single lock inside the interpreter, and a thread must hold it to run Python bytecode. Only one thread can hold it at a time. So in a normal Python build, **only one thread executes Python code at any instant**, no matter how many cores you have.

Why would anyone design it that way? Because the interpreter's own data must stay consistent. Every Python object has a **reference count** (how many names point at it), and the interpreter changes those counts constantly. If two threads changed the same count at the same time, it could go wrong, and an object could be freed while still in use, crashing the program. One big lock was the simplest way to keep the interpreter safe, and it makes single-threaded code fast, because there is no locking cost on every object.

```python
import sys

print("GIL enabled:", sys._is_gil_enabled())
print("switch interval:", sys.getswitchinterval(), "seconds")
```
```text
GIL enabled: True
switch interval: 0.005 seconds
```

### 4.2 When the GIL is released

If one thread held the GIL forever, other threads would never run. Two rules make threads take turns:

1. **Blocking I/O releases the GIL.** When a thread calls `time.sleep`, reads from a socket, waits for a file, or waits for a lock, it hands the GIL to someone else first. That is why threads work so well for I/O: while one thread waits for the network, another runs.
2. **The switch interval.** A thread that computes without stopping is asked to give up the GIL every 5 milliseconds (`sys.getswitchinterval()`), so other threads get a turn.

Many C extensions also release the GIL during long calculations: `hashlib` on big inputs, `zlib` compression, NumPy on large arrays. Threads can give a real speed-up there, because the heavy work happens in C, outside the GIL.

A quick check: ten threads that each `time.sleep(0.3)` (started together, then joined) took **0.30 s** in total on the test machine (your times will differ). Ten waits overlapped perfectly. Compare with the prime counting in section 1.2, where threads gave nothing: pure Python computation never releases the GIL except at the switch interval, so the threads just take turns.

### 4.3 What the GIL does *not* protect

A very common myth: "Python has a GIL, so I do not need locks." Wrong. The GIL keeps the **interpreter** safe. It does not keep **your data** safe. Look at what `counter += 1` really is:

```python
import dis

counter = 0

def increment():
    global counter
    counter += 1

dis.dis(increment)
```
```text
  5           RESUME                   0

  7           LOAD_GLOBAL              0 (counter)
              LOAD_SMALL_INT           1
              BINARY_OP               13 (+=)
              STORE_GLOBAL             0 (counter)
              LOAD_CONST               1 (None)
              RETURN_VALUE
```

One line of Python is **several bytecode steps**: load the value, add 1, store the result. A thread can lose the GIL between any two steps. If thread A loads `counter` (say 5), then loses the GIL, then thread B loads 5, adds 1, stores 6, and then A continues, adds 1 to *its* 5 and stores 6, one increment is lost. Section 5 shows this happening.

Recent CPython versions switch threads less often in the middle of such short lines, so a simple `counter += 1` loop may *happen* to give the right total on your machine today. That is luck, not safety: a different Python version, a busier machine, or a free-threaded build can break it. Code that is correct only because of how often the interpreter happens to switch is wrong.

### 4.4 Free-threaded Python (3.13t, 3.14t)

Since Python 3.13 there is a second build of CPython **without the GIL**, called the **free-threaded** build. Its executable is usually named `python3.13t` or `python3.14t`. In 3.13 it was experimental; in 3.14 it is officially supported, though still optional. You install it separately (for example the "free-threaded" option in the python.org installer, or `uv python install 3.14t`).

In a free-threaded build, threads really run Python code in parallel on several cores, so the prime-counting example in section 1.2 *would* speed up with threads. The cost: single-threaded code runs somewhat slower, and some C extension packages are not ready yet (if you import one, the interpreter may switch the GIL back on and print a warning).

You can check at run time with `sys._is_gil_enabled()` (`True` on normal builds, `False` on free-threaded ones). For this course, two lessons matter:

1. Everything in this chapter is correct on both builds. **Locks are needed on both.** Without the GIL, races become *more* frequent, not less.
2. "Use processes for CPU-bound work" is the rule today. Free threading may change that in the coming years. That is one more reason to write code that is correct by design (locks, queues, no shared mutable state) rather than code that relies on the GIL.

#### Try it 4.1

Explain in two or three sentences why ten threads that each `time.sleep(1)` finish in about 1 second in total, but ten threads that each run a 1-second pure-Python loop take about 10 seconds (normal GIL build).

<details><summary>Answer</summary>

A sleeping thread releases the GIL and needs no CPU, so all ten sleeps overlap and finish together after about 1 second. A thread running a Python loop needs the GIL for every bytecode step, and only one thread can hold the GIL at a time, so the ten loops take turns and their run times add up to about 10 seconds (often a bit more, because of switching).

</details>

## 5. Race conditions, `Lock` and `RLock`

### 5.1 What a race condition is

A **race condition** is a bug where the result depends on the exact timing of threads: who runs first, who gets paused where. The program may give the right answer 999 times and the wrong answer once. These bugs are hard because they are **not reproducible on demand**, the first step of the debugging loop from chapter 20.

Every race has the same shape. Two or more threads touch the **same shared data**, at least one of them **writes**, and the operation takes **several steps** that another thread can sneak in between. The classic form is **read–modify–write**:

```text
   balance = 0
   thread A                    thread B
   read balance   -> 0
                               read balance   -> 0
   write 0 + 100  -> 100
                               write 0 + 100  -> 100    (A's deposit is lost)
```

### 5.2 Making a race happen every time

Real races depend on luck, which makes them bad for teaching. So in this chapter we **force** them: we put a small pause exactly in the gap between the read and the write. The pause stands for "a slow step", such as a database call or a log write, and it guarantees that the other threads run in the gap:

```python
import threading
import time

balance = 0

def deposit(amount):
    global balance
    current = balance          # 1. read
    time.sleep(0.05)           # 2. a slow step: other threads run here
    balance = current + amount # 3. write

threads = [threading.Thread(target=deposit, args=(100,)) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("expected 1000, got", balance)
```
```text
expected 1000, got 100
```

All ten threads read `0` during the pause, and each wrote `0 + 100`. Nine deposits vanished. Remove the `sleep` and you will usually get 1000, which is worse: the bug is still there, it just hides.

Even `time.sleep(0)`, a pause of zero seconds, is enough, because it makes the thread give up the GIL. A counter class whose `increment()` does `v = self._value; time.sleep(0); self._value = v + 1`, used by 8 threads that each increment 200 times, should reach 1,600. Runs on the test machine printed 208, 203, 209 and 213: a different wrong number every time.

### 5.3 The fix: a lock

A `threading.Lock` is a token that only one thread can hold at a time. `acquire()` takes it (waiting if another thread has it); `release()` gives it back. The code between them is called a **critical section**: only one thread at a time can be inside it.

Always use a lock with `with`. It acquires on entry and releases on exit, **even if an exception is raised** inside. The usual style is to keep the lock **inside the object** whose data it protects, so callers cannot forget it. Here is the counter, fixed, with the same `sleep(0)` gap still inside:

```python
import threading
import time

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            v = self._value
            time.sleep(0)
            self._value = v + 1

    @property
    def value(self):
        with self._lock:
            return self._value

c = Counter()

def work():
    for _ in range(200):
        c.increment()

threads = [threading.Thread(target=work) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(c.value)
```
```text
1600
```

### 5.4 Rules for critical sections

1. **Every** access to the shared data goes through the same lock, reads included. A lock that only some code uses protects nothing. Reading without the lock can see a half-updated state (for example, after one of two related fields has changed).
2. **Keep critical sections short.** While one thread holds the lock, all others that need it wait. Do the slow work (network calls, file reads) *outside* the lock and lock only the update of shared data. (The demo above kept the `sleep` inside on purpose, to show the race was fixed.)
3. **Never call unknown code while holding a lock**: callbacks, user functions, logging handlers that might take other locks. That is how deadlocks start (section 6).
4. **One lock per piece of shared state**, owned by the object that owns the state.

### 5.5 Check-then-act races

Read–modify–write is one race shape. **Check-then-act** is the other: a thread checks a condition, then acts on it, but the condition changed in between.

```python
import threading
import time

seats = {"A1": None}

def book(seat, person):
    if seats[seat] is None:       # check
        time.sleep(0.05)          # slow step: the other thread runs here
        seats[seat] = person      # act
        print(f"{person} booked {seat}")

threads = [threading.Thread(target=book, args=("A1", p)) for p in ["Asha", "Ravi"]]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(seats)
```
```text
Asha booked A1
Ravi booked A1
{'A1': 'Ravi'}
```

Both were told they booked the seat; only one has it. The fix is the same: the check and the act must be in **one** critical section, so nothing can change in between.

### 5.6 Myths about "atomic" operations

An operation is **atomic** if no other thread can see it half-done. Under the GIL, some single operations on built-in types happen to be atomic: `list.append`, `dict[key] = value`, `list.pop()`. People then build on that and write `if key not in d: d[key] = compute()`, which is check-then-act and not atomic at all.

Simple rule for this course: **if more than one thread writes shared data, use a lock**, unless you use a structure made for threads, such as `queue.Queue` (section 7.5). Do not reason about which bytecodes are atomic; it changes between Python versions and is different on free-threaded builds.

### 5.7 `Lock` methods and `RLock`

Besides `with`, a lock has a few methods, each checked on the test machine:

- `lock.acquire()` waits until it gets the lock and returns `True`.
- `lock.acquire(blocking=False)` returns `False` at once if the lock is taken.
- `lock.acquire(timeout=0.1)` waits up to 0.1 s, then returns `False`.
- `lock.locked()` tells whether someone holds it (a snapshot that may be stale a moment later).
- `lock.release()` on a lock that is not held raises `RuntimeError: release unlocked lock`.

A plain `Lock` does not remember **who** holds it. If the thread that holds it tries to acquire it again, it waits for itself, forever. An **`RLock`** (re-entrant lock) remembers its owner and a count: the owner may acquire it again, and it is really released when the count drops back to zero. That is useful when one locked method calls another locked method of the same object:

```python
class Inventory:
    def __init__(self):
        self._lock = threading.RLock()
        self._stock = {}

    def add(self, item, qty):
        with self._lock:
            self._stock[item] = self._stock.get(item, 0) + qty

    def add_many(self, pairs):
        with self._lock:              # holds the lock...
            for item, qty in pairs:
                self.add(item, qty)   # ...and add() takes it again: fine with RLock
```

`add_many([("pen", 3), ("book", 1), ("pen", 2)])` leaves `{'pen': 5, 'book': 1}`. With `threading.Lock()` instead, `add_many` would freeze on its first call to `add`. An alternative many people prefer is a private helper that assumes the lock is already held (`_add_unlocked`), called by both public methods. It makes the locking clearer and works with a plain `Lock`.

#### Try it 5.1 (Predict the output)

```python
import threading

lock = threading.Lock()
rlock = threading.RLock()

with rlock:
    print(rlock.acquire(timeout=0.1))
    rlock.release()

with lock:
    print(lock.acquire(timeout=0.1))
print("done")
```

<details><summary>Answer</summary>

```text
True
False
done
```

The `RLock` is already held by this thread, so acquiring it again succeeds at once (the count goes to 2, and `release()` brings it back to 1). The plain `Lock` is held too, and it does not care who holds it: the second `acquire` waits 0.1 s and gives up with `False`. Without the timeout, the program would hang forever right there.

</details>

#### Try it 5.2

A shared account starts at 100. Three threads call `withdraw(70)` at the same time. `withdraw` checks `if self.balance >= amount`, then does a slow bank call, then subtracts. (a) Without a lock, what results and final balance are possible? (b) Where must the lock go?

<details><summary>Answer</summary>

(a) All three can pass the check before anyone subtracts, so all three return `True` and the balance ends at **-110**; other interleavings give two successes and -40. (b) The check **and** the subtraction must be inside one `with self._lock:` block. With that, a test run printed `[False, False, True] 30`: exactly one withdrawal succeeds. Locking only the subtraction is not enough; the check-then-act gap remains.

</details>

## 6. Deadlocks

### 6.1 Two threads, two locks, no progress

A **deadlock** is when threads wait for each other in a circle, so none of them can ever continue. The program does not crash and does not use CPU. It just stops, forever.

The classic case: thread 1 holds lock A and wants lock B; thread 2 holds lock B and wants lock A.

```python
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker_1():
    with lock_a:
        time.sleep(0.05)        # worker_2 grabs lock_b meanwhile
        with lock_b:
            print("worker_1 got both")

def worker_2():
    with lock_b:
        time.sleep(0.05)        # worker_1 grabs lock_a meanwhile
        with lock_a:
            print("worker_2 got both")

t1 = threading.Thread(target=worker_1, daemon=True)
t2 = threading.Thread(target=worker_2, daemon=True)
t1.start()
t2.start()
t1.join(timeout=1)
t2.join(timeout=1)
print("still alive after 1 s:", t1.is_alive(), t2.is_alive())
```
```text
still alive after 1 s: True True
```

Neither "got both" line ever prints. (We used daemon threads and `join(timeout=1)` only so this demo can exit; a real deadlocked program just hangs. `join(timeout=...)` returns after the timeout whether or not the thread finished, so you must check `is_alive()` afterwards.)

Four conditions must all be true for a deadlock: (1) a lock can be held by only one thread, (2) a thread holds one lock while waiting for another, (3) nobody can take a lock away from its holder, and (4) there is a **circle** of waiting. Breaking any one prevents deadlock. In practice we break the circle.

### 6.2 Fix 1: always take locks in the same order

If every thread takes locks in the **same global order**, a circle is impossible: whoever gets the first lock will also get the second. A bank transfer locks two accounts; order them by account number, not by "source then destination":

```python
class Account:
    def __init__(self, number, balance):
        self.number = number
        self.balance = balance
        self.lock = threading.Lock()

def transfer(src, dst, amount):
    # Always lock the account with the smaller number first.
    first, second = sorted([src, dst], key=lambda acc: acc.number)
    with first.lock:
        time.sleep(0.05)
        with second.lock:
            src.balance -= amount
            dst.balance += amount
```

Running `transfer(a, b, 100)` and `transfer(b, a, 30)` at the same time, on accounts 1 and 2 with 500 each, in daemon threads joined with a 2 s timeout:

```text
finished: True
balances: 430 570 total: 1000
```

Both transfers finished, and money was conserved (the total is still 1000), which is the invariant to check in any banking test.

### 6.3 Fix 2: do not hold one lock while taking another

Often the simplest fix is design: do not nest locks at all. Copy the data you need under lock A, release it, then work with lock B. Or use **one** lock for data that is always changed together.

### 6.4 Self-deadlock

The smallest deadlock needs only one thread and one plain `Lock`: a function holding the lock calls another function that does `with lock:` again. A plain `Lock` does not know who holds it, so the thread waits for itself. In a test, a thread running `outer()` below was still alive (`stuck: True`) after `join(timeout=0.5)`:

```python
lock = threading.Lock()

def outer():
    with lock:
        inner()

def inner():
    with lock:              # same thread, same Lock: waits for itself forever
        print("never printed")
```

The fixes are the ones from section 5.7: use an `RLock`, or split the code into a locked public method and an unlocked private helper.

### 6.5 Fix 3: give up and retry with `acquire(timeout=...)`

If you cannot control the order, a thread can try the second lock with a timeout (`if second.acquire(timeout=0.1): ...`). If it fails, it **releases everything it holds**, waits a little and tries again. This works, but it is more complex and wastes time; lock ordering is better whenever you can use it. If both threads back off for exactly the same time, they can collide again and again: a **livelock**. Random or different back-off times prevent it.

### 6.6 Finding a deadlock

A frozen program with 0% CPU is the symptom. To see **where** each thread is stuck, ask Python to print every thread's stack. Add these lines at the end of the deadlock program from section 6.1 (replacing the joins), so they run while the two workers are stuck:

```python
import faulthandler
import sys

time.sleep(0.3)
faulthandler.dump_traceback(file=sys.stdout, all_threads=True)
```
```text
Thread 0x00007463de3486c0 [Thread-2 (worke] (most recent call first):
  File "/home/you/conc/dump.py", line 16 in worker_2
  File "/usr/lib/python3.14/threading.py", line 1024 in run
  File "/usr/lib/python3.14/threading.py", line 1082 in _bootstrap_inner
  File "/usr/lib/python3.14/threading.py", line 1044 in _bootstrap

Thread 0x00007463deb496c0 [Thread-1 (worke] (most recent call first):
  File "/home/you/conc/dump.py", line 10 in worker_1
  File "/usr/lib/python3.14/threading.py", line 1024 in run
  File "/usr/lib/python3.14/threading.py", line 1082 in _bootstrap_inner
  File "/usr/lib/python3.14/threading.py", line 1044 in _bootstrap

Current thread 0x00007463df02a200 [python] (most recent call first):
  File "/home/you/conc/dump.py", line 28 in <module>
```

(The thread addresses are machine-specific.) Line 10 is `with lock_b:` in `worker_1`; line 16 is `with lock_a:` in `worker_2`. Each thread is stuck taking the lock the other one holds: the circle is right there.

In a program that is already hung, you can get the same dump without changing code:

- Start it with `python -X faulthandler app.py`, or call `faulthandler.register(signal.SIGUSR1)` at start-up, then send that signal (`kill -USR1 <pid>`) when it hangs (Linux/macOS).
- Use `py-spy dump --pid <pid>` (a separate tool, `pip install py-spy`), which works on any running Python program.
- In tests, never wait forever: `join(timeout=...)` and assert `not t.is_alive()`, so a deadlock becomes a failing test instead of a frozen test run.

#### Try it 6.1

A function moves stock between warehouses: `move(src, dst, qty)` does `with src.lock: with dst.lock: ...`. Two threads run `move(w1, w2, 5)` and `move(w2, w1, 3)` at the same time and the program sometimes freezes. Explain why in one sentence, and give the one-line change that fixes it, assuming every warehouse has a unique `code` string.

<details><summary>Answer</summary>

Each thread can take its first lock (`w1` and `w2`), then wait forever for the lock the other holds: a circle of waiting. Fix: lock in a fixed global order, for example

```python
first, second = sorted([src, dst], key=lambda w: w.code)
```

and then `with first.lock: with second.lock: ...`. Now both threads take the lock with the smaller code first, so a circle cannot form.

</details>

## 7. Coordinating threads: events, semaphores, conditions, queues

Locks protect data. The tools in this section answer a different question: **how do threads tell each other things?** "The config is ready." "Stop now." "At most three of you at once." "Here is the next job."

### 7.1 `Event`: a flag threads can wait for

An `Event` is a true/false flag. `set()` makes it true, `clear()` makes it false, `is_set()` reads it, and `wait()` blocks until it is true. A typical use is "wait until the config is loaded": the server thread calls `ready.wait()`, the loader thread fills the config and calls `ready.set()`, and the server continues.

The most common use of an event is a **stop signal** for a background thread. The key trick: wait on the event **instead of** `time.sleep`. `stop.wait(1.0)` sleeps up to one second, but wakes up the moment someone calls `stop.set()`:

```python
import threading
import time

stop = threading.Event()

def poller():
    checks = 0
    while not stop.is_set():
        checks += 1
        stop.wait(1.0)           # sleeps up to 1 s, wakes AT ONCE when stop is set
    print(f"poller: stopped after {checks} check(s)")

t = threading.Thread(target=poller)
t.start()
time.sleep(0.2)
start = time.perf_counter()
stop.set()
t.join()
print(f"stop took {time.perf_counter() - start:.3f} s")
```
```text
poller: stopped after 1 check(s)
stop took 0.001 s
```

(Your times will differ.) With `time.sleep(1.0)` in the loop, stopping could take a full second. With a 60-second interval, a minute. `Event.wait(timeout)` returns `True` if the event was set and `False` if it timed out, so you can also write `while not stop.wait(interval): do_work()`.

### 7.2 `Semaphore`: at most N at once

A **semaphore** is a counter of free slots. `acquire()` takes a slot, waiting if there are none; `release()` gives one back. `Semaphore(3)` lets at most 3 threads into a section at the same time. This is how you stop 100 threads from opening 100 connections to a server that allows 3:

```python
import threading
import time

slots = threading.Semaphore(3)       # at most 3 at once
lock = threading.Lock()
running = 0
peak = 0

def download(n):
    global running, peak
    with slots:
        with lock:
            running += 1
            peak = max(peak, running)
        time.sleep(0.1)
        with lock:
            running -= 1

threads = [threading.Thread(target=download, args=(n,)) for n in range(10)]
start = time.perf_counter()
for t in threads:
    t.start()
for t in threads:
    t.join()
print("peak running:", peak)
print(f"took {time.perf_counter() - start:.2f} s")
```
```text
peak running: 3
took 0.40 s
```

(Your times will differ.) Ten jobs, three at a time, 0.1 s each: four "waves" (3 + 3 + 3 + 1), about 0.4 s. Notice the **peak counter**: a `running` count protected by a lock, increased when work starts and decreased when it ends, with the highest value remembered. This is the standard way to *test* a concurrency limit. Counting is reliable; timing is not.

A `BoundedSemaphore` is the same, but it raises `ValueError: Semaphore released too many times` if you release more often than you acquired. A plain `Semaphore` would silently grow to allow one more thread, hiding the bug. Prefer `BoundedSemaphore` for limits, and use `with` so you cannot forget a release.

### 7.3 `Condition`: wait until something is true

An `Event` is one flag. Sometimes a thread must wait for a more complex state: "until there are at least two orders", "until the buffer has space". A **`Condition`** combines a lock with a way to sleep until notified:

```python
import threading
import time

orders = []
cond = threading.Condition()

def cook():
    with cond:
        cond.wait_for(lambda: len(orders) >= 2)   # releases the lock while waiting
        print("cook: got", orders)

def waiter(dish):
    with cond:
        orders.append(dish)
        print("waiter: added", dish)
        cond.notify_all()

c = threading.Thread(target=cook)
c.start()
for dish in ["dosa", "idli"]:
    time.sleep(0.05)
    w = threading.Thread(target=waiter, args=(dish,))
    w.start()
    w.join()
c.join()
```
```text
waiter: added dosa
waiter: added idli
cook: got ['dosa', 'idli']
```

How it works:

- `with cond:` takes the condition's lock.
- `cond.wait_for(predicate)` checks the predicate. If it is false, it **releases the lock** and sleeps. When notified, it wakes, takes the lock back, and checks the predicate again. It returns only when the predicate is true, while holding the lock.
- `notify_all()` (or `notify()` for one waiter) wakes the waiters. It must be called while holding the lock, after changing the state.

Always use `wait_for` with a predicate (or `wait()` inside a `while` loop), never a bare `wait()` inside an `if`: a waiting thread can wake up when the state is still not what it wants. `wait_for(pred, timeout=...)` returns the predicate's last value, so `False` means "timed out". Problem p046 builds a bounded buffer with a `Condition`.

### 7.4 `Barrier`: wait until everyone arrives

A **`Barrier(n)`** makes `n` threads wait for each other: each calls `barrier.wait()`, and nobody passes until all `n` have arrived. It is handy in tests and benchmarks to start several workers at exactly the same moment, which makes races more likely to show up.

### 7.5 `queue.Queue`: the safest way to share work

Most thread bugs come from **shared mutable data**. The cleanest design avoids sharing altogether: threads **send messages** to each other through a queue. `queue.Queue` is built for threads. Its `put` and `get` are internally locked, and `get()` waits until an item is available.

The **producer–consumer** pattern: one part of the program puts jobs into a queue, a few worker threads take them out and process them.

```python
import queue
import threading
import time

STOP = None                       # the sentinel
tasks = queue.Queue()
results = queue.Queue()

def worker(name):
    while True:
        item = tasks.get()
        if item is STOP:
            break
        time.sleep(0.1)           # pretend work
        results.put((item, item * item, name))

workers = [threading.Thread(target=worker, args=(f"w{i}",)) for i in range(3)]
for w in workers:
    w.start()

start = time.perf_counter()
for n in range(6):
    tasks.put(n)
for _ in workers:
    tasks.put(STOP)               # one sentinel per worker
for w in workers:
    w.join()

out = sorted(results.get() for _ in range(results.qsize()))
print([(item, sq) for item, sq, _ in out])
print(f"took {time.perf_counter() - start:.2f} s")
```
```text
[(0, 0), (1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]
took 0.20 s
```

(Your times will differ.) Six jobs, three workers, 0.1 s each: about 0.2 s.

The **sentinel** is a special value meaning "no more work". Each worker stops when it receives one, so you need **one sentinel per worker**. If you put only one, the first worker to get it stops, and the others wait on `tasks.get()` forever. The program never exits.

Results arrive in completion order. To return them in input order, send the index with the item (`(index, item)`) and put the result into slot `index` of a list, or sort by index at the end, as above.

### 7.6 `task_done()` and `join()`

A second way to know when all work is finished: every `get()` is matched by a `task_done()` call, and `q.join()` waits until the count of unfinished items drops to zero (here `q = queue.Queue()` and `done = []`):

```python
def worker():
    while True:
        item = q.get()
        done.append(item.upper())
        q.task_done()             # one task_done() for every get()

threading.Thread(target=worker, daemon=True).start()
for word in ["a", "b", "c"]:
    q.put(word)
q.join()                          # waits until every item had task_done()
print(done)                       # ['A', 'B', 'C']
```

Here the worker loops forever, so it is a daemon thread that dies when the program ends. Put `task_done()` in a `finally:` block if the work can raise, otherwise one exception leaves the count stuck and `join()` waits forever.

### 7.7 Kinds of queues

Putting 3, 1, 2 into each kind and taking three items out gives:

```text
Queue          [3, 1, 2]    first in, first out
LifoQueue      [2, 1, 3]    last in, first out (a stack)
PriorityQueue  [1, 2, 3]    smallest first: put tuples like (priority, job)
```

- `maxsize` makes a **bounded** queue: `put()` blocks while it is full. That is **backpressure**: a fast producer is slowed down to the speed of the consumers instead of filling memory.
- `put_nowait(x)` on a full queue raises `queue.Full`; `get_nowait()` on an empty queue raises `queue.Empty`; `get(timeout=0.1)` waits 0.1 s and then raises `queue.Empty`.
- `qsize()` is only a snapshot: by the time you act on it, another thread may have changed the queue. Do not write `if q.qsize() > 0: q.get()` across threads; use `get(timeout=...)` and catch `queue.Empty`.

#### Try it 7.1 (Predict the output)

Five jobs, each sleeping 0.1 s, run in five threads that all use `with slots:` around the sleep, where `slots = threading.Semaphore(2)`. About how long does the whole run take, and what is the highest number of jobs ever sleeping at the same time?

<details><summary>Answer</summary>

About **0.3 s**, with a peak of **2**. Two jobs run, then two more, then the last one: three waves of 0.1 s. A test run printed `0.3 s` (your times will differ).

</details>

#### Try it 7.2

Three worker threads read from a `queue.Queue` and stop when they get `None`. The main thread puts 10 jobs, then **one** `None`, then joins all three workers. What happens, and how do you fix it?

<details><summary>Answer</summary>

The program **hangs**. The first worker to reach `None` stops; the other two finish the remaining jobs and then block on `tasks.get()` forever, so the main thread's `join()` never returns. Fix: put one sentinel **per worker** (`for _ in workers: tasks.put(None)`). Another fix is to make workers daemons and use `task_done()` + `tasks.join()`, but then the workers are never cleanly stopped.

</details>

## 8. `multiprocessing`

### 8.1 Why processes

Threads cannot run Python code in parallel on a normal build (section 4). Processes can: each has its own interpreter and its own GIL. The price is that processes **do not share memory** (section 2.2), so everything you send to a process and everything it sends back must be **copied**, by turning it into bytes (pickling) and back.

### 8.2 `Process`

`multiprocessing.Process` has the same shape as `Thread`: `target`, `args`, `start()`, `join()`.

```python
import multiprocessing
import os

def report(label):
    print(f"{label}: pid={os.getpid()} parent={os.getppid()}")

if __name__ == "__main__":
    report("main")
    p = multiprocessing.Process(target=report, args=("child",))
    p.start()
    p.join()
    print("child exit code:", p.exitcode)
```
```text
main: pid=12028 parent=12027
child: pid=12031 parent=12030
child exit code: 0
```

(The pids are machine-specific.) The child's parent is not the main program but a helper process, the **fork server**, which is how Python 3.14 starts processes on Linux (section 8.4). `exitcode` is 0 for success; a child that died from an uncaught exception has exit code 1, and the exception is printed by the child, not raised in the parent, just like with threads.

### 8.3 The `if __name__ == "__main__":` guard

When Python starts a child process with the *spawn* or *forkserver* method, the child **imports your main file** to find the target function. Importing runs every top-level line. Without the guard, the child would try to start its own child, which would start another... Python detects this and stops:

```python
import multiprocessing

print("top of file, running as", __name__)

def hello():
    print("hello from the child")

p = multiprocessing.Process(target=hello)
p.start()
p.join()
```
```text
top of file, running as __main__
top of file, running as __mp_main__
Traceback (most recent call last):
  ...
RuntimeError:
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.
        ...
            if __name__ == '__main__':
                freeze_support()
                ...
```

(The full output is two long tracebacks; this is the important part.) The second line shows the child importing the file under the name `__mp_main__`, so a guard `if __name__ == "__main__":` is false in the child. **Rule: in any program that starts processes, put the starting code under the guard, and keep the worker functions at the top level of the module.**

### 8.4 Start methods

There are three ways to create a child process:

| Method | How | Default on |
|---|---|---|
| `spawn` | start a fresh Python, import the main module, receive the function and arguments by pickling | Windows, macOS |
| `fork` | copy the parent process exactly as it is (memory, open files, all) | (older Linux Pythons) |
| `forkserver` | start one clean server process early; fork each child from that server | Linux, Python 3.14+ |

On the test machine (Linux, Python 3.14), `multiprocessing.get_all_start_methods()` returned `['forkserver', 'fork', 'spawn']` and `multiprocessing.get_start_method()` returned `'forkserver'`.

`fork` is fast, but copying a process that has running threads is dangerous: a lock held by another thread at the moment of the fork is copied in its locked state, and no thread in the child will ever release it. That is why Python moved Linux to `forkserver` in 3.14. You can choose a method with `multiprocessing.get_context("spawn")`, but the safe habit is: **write code that works with `spawn`** (guard, top-level functions, picklable arguments), and it will work everywhere.

### 8.5 Pickling and `Pool`

Arguments and return values travel between processes as **pickles** (`pickle.dumps` turns an object into bytes, `pickle.loads` turns them back). Functions are pickled **by name**: the pickle says "the function `square` in module `__main__`", and the child looks that name up. So only things that can be found by name can be sent:

```python
import pickle
import threading

def double(x):
    return x * 2

for obj in [double, [1, "two", 3.0], lambda x: x, threading.Lock()]:
    try:
        data = pickle.dumps(obj)
        print("ok      ", type(obj).__name__, len(data), "bytes")
    except Exception as e:
        print("FAILS   ", type(obj).__name__, "->", type(e).__name__)
```
```text
ok       function 34 bytes
ok       list 33 bytes
FAILS    function -> PicklingError
FAILS    lock -> TypeError
```

A top-level function pickles as a short name (34 bytes). A lambda has no name to look up, and a lock or an open file belongs to *this* process and cannot be moved. That is why the classic mistake `pool.map(lambda x: x * 2, [1, 2, 3])` fails with `PicklingError: Can't pickle <function <lambda> ...>: it's not found as __main__.<lambda>`. Fix: define `def double(x): return x * 2` at the top level and pass `double`.

A `Pool` keeps a fixed set of worker processes and hands them jobs, so you pay the start-up cost once:

```python
from multiprocessing import Pool

def square(x):
    return x * x

def power(base, exp):
    return base ** exp

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        print(pool.map(square, range(10)))
        print(pool.starmap(power, [(2, 3), (3, 2), (10, 4)]))
```
```text
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
[8, 9, 10000]
```

`map` returns results in input order; `starmap` unpacks tuples into arguments; `imap_unordered` yields results as they finish. For new code, `ProcessPoolExecutor` (section 9) gives the same power with a nicer interface.

**Keep the data small and the work big.** Sending a 100 MB list to a worker costs more than many calculations. Send file names, not file contents, and give each job enough work (thousands of items, not one) to be worth the trip.

### 8.6 Sharing state between processes

A global variable changed in a child is changed only in the child. To really share a number, use `multiprocessing.Value`, which lives in shared memory:

```python
import multiprocessing

hits = 0                               # an ordinary global

def count_global(n):
    global hits
    for _ in range(n):
        hits += 1

def count_shared(counter, n):
    for _ in range(n):
        with counter.get_lock():       # += on a Value is NOT atomic
            counter.value += 1

if __name__ == "__main__":
    procs = [multiprocessing.Process(target=count_global, args=(1000,)) for _ in range(2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print("global in parent:", hits)

    counter = multiprocessing.Value("i", 0)      # "i" = C int, in shared memory
    procs = [multiprocessing.Process(target=count_shared, args=(counter, 1000)) for _ in range(2)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print("shared Value:", counter.value)
```
```text
global in parent: 0
shared Value: 2000
```

Processes run truly in parallel, so a race on `counter.value += 1` is real; `get_lock()` returns the lock that comes with the `Value`. Pass the `Value` to the child as an **argument**; do not rely on a global.

`multiprocessing.Array("i", n)` is a fixed-size shared array of C numbers: two processes filling halves of `Array("i", 6)` with squares left `[0, 1, 4, 9, 16, 25]` in the parent. A `Manager` (`with multiprocessing.Manager() as m: d = m.dict()`) runs a small server process that holds ordinary Python objects and lets other processes change them through proxies. It is flexible but slow, because every access is a message.

The best design, as with threads, is to **share nothing**: give each process its input, let it return its result, and combine the results in the parent. `multiprocessing.Queue` (same interface as `queue.Queue`, but between processes) is the tool when you need a stream of messages.

#### Try it 8.1

Which of these can be passed to a process pool as the function or as an argument? A top-level function; a function defined inside another function; a bound method `Greeter().hello` of a top-level class; a tuple of ints; an open file object.

<details><summary>Answer</summary>

Checked with `pickle.dumps`:

```text
top-level function: ok
nested function: PicklingError
bound method: ok
tuple of ints: ok
open file: TypeError
```

A nested function cannot be found by name from the module's top level. A bound method pickles as "the instance (pickled normally) plus the method name", so it works if the instance can be pickled. An open file belongs to this process; send the **file name** instead and let the worker open it.

</details>

## 9. `concurrent.futures`

### 9.1 Executors and futures

Starting threads by hand, collecting results into lists, catching exceptions inside targets: you have done all of that, and it is repetitive. The `concurrent.futures` module packages it:

- An **executor** is a pool of workers. `ThreadPoolExecutor` uses threads; `ProcessPoolExecutor` uses processes. **Same interface**, so switching between them is one word.
- `executor.submit(fn, *args)` schedules one call and returns at once with a **future**.
- A **future** is a box that will hold the result later. `future.result()` waits for it and returns it, or **re-raises** the exception the call raised.

```python
import time
from concurrent.futures import ThreadPoolExecutor

def slow_square(n):
    time.sleep(0.2)
    return n * n

with ThreadPoolExecutor(max_workers=2) as pool:
    fut = pool.submit(slow_square, 7)
    print(fut.done())
    print(fut.result())          # waits here
    print(fut.done())
```
```text
False
49
True
```

The `with` block calls `pool.shutdown(wait=True)` on exit: it waits for all submitted work to finish and stops the workers. Always use executors with `with` (or call `shutdown` yourself), so no worker is left behind.

`max_workers` matters. For threads doing I/O, 5–32 is common (the default is `min(32, cpu_count + 4)`). For processes doing CPU work, the default is the number of cores, and more does not help.

### 9.2 `map` (input order) and `as_completed` (completion order)

`executor.map(fn, items)` is like the built-in `map`, but concurrent. Results come back **in input order**, even if later items finish first. To handle each result as soon as it is ready (to show progress, or to start the next step early), submit futures and loop over `as_completed`. This example does both, with a job where **small numbers are slower**:

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def slow_square(n):
    time.sleep(0.1 * (5 - n))    # small n are SLOWER
    return n * n

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as pool:
    for result in pool.map(slow_square, [1, 2, 3, 4]):
        print(f"map  {time.perf_counter() - start:.1f}s  {result}")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(slow_square, n): n for n in [1, 2, 3, 4]}
    for fut in as_completed(futures):
        n = futures[fut]
        print(f"asc  {time.perf_counter() - start:.1f}s  {n} -> {fut.result()}")
```
```text
map  0.4s  1
map  0.4s  4
map  0.4s  9
map  0.4s  16
asc  0.1s  4 -> 16
asc  0.2s  3 -> 9
asc  0.3s  2 -> 4
asc  0.4s  1 -> 1
```

(Your times will differ.) With `map`, item 1 was the slowest and comes first, so nothing could be printed before 0.4 s. With `as_completed`, each result appeared as soon as it was ready. The dict `{future: input}` is the standard trick to remember which input each future belongs to, because `as_completed` gives you futures in a new order.

### 9.3 Exceptions

A future stores the exception instead of losing it:

```python
from concurrent.futures import ThreadPoolExecutor

def parse(text):
    return int(text)

with ThreadPoolExecutor(max_workers=2) as pool:
    good = pool.submit(parse, "42")
    bad = pool.submit(parse, "forty")
    print(good.result())
    print(repr(bad.exception()))
    try:
        bad.result()
    except ValueError as e:
        print("result() re-raised:", e)

    results = pool.map(parse, ["1", "x", "3"])
    print(next(results))
    try:
        print(next(results))
    except ValueError as e:
        print("map raised at item 2:", e)
```
```text
42
ValueError("invalid literal for int() with base 10: 'forty'")
result() re-raised: invalid literal for int() with base 10: 'forty'
1
map raised at item 2: invalid literal for int() with base 10: 'x'
```

- `future.exception()` returns the exception (or `None`) without raising.
- `future.result()` re-raises it in **your** thread, with its traceback.
- `map` raises when your loop **reaches** the bad item. Earlier results were already delivered; later ones are lost from the iteration. If you need every result *and* every error, use `submit` and check each future.

If you never call `result()` or `exception()`, the error is silently ignored. Futures make errors *available*; you still have to look.

### 9.4 `wait`, timeouts and cancelling

`concurrent.futures.wait(futures, timeout=None, return_when=...)` returns two sets, `(done, not_done)`. `return_when` can be `ALL_COMPLETED` (default), `FIRST_COMPLETED` or `FIRST_EXCEPTION`. With three jobs of 0.3 s, 0.1 s and 0.2 s, `wait(futures, return_when=FIRST_COMPLETED)` returned after about 0.1 s with only the fast one in `done` and 2 in `not_done`. With `timeout=...` it returns whatever is done when time is up.

`future.result(timeout=...)` also accepts a timeout and raises `TimeoutError` if the result is not ready. Note that a timeout only stops **you** from waiting: the call keeps running in its worker.

`future.cancel()` can only stop a call that **has not started yet** (still waiting in the queue). A running call cannot be interrupted:

```python
import time
from concurrent.futures import ThreadPoolExecutor

started = []

def job(n):
    started.append(n)
    time.sleep(0.1)
    return n

with ThreadPoolExecutor(max_workers=1) as pool:
    futures = [pool.submit(job, n) for n in range(4)]
    time.sleep(0.02)               # job 0 is running now
    print("cancel running job 0:", futures[0].cancel())
    print("cancel queued job 2: ", futures[2].cancel())
print("states:", [("cancelled" if f.cancelled() else f.result()) for f in futures])
print("started:", started)
```
```text
cancel running job 0: False
cancel queued job 2:  True
states: [0, 1, 'cancelled', 3]
started: [0, 1, 3]
```

To drop all queued work at once, for example after the first error, use `pool.shutdown(wait=True, cancel_futures=True)`. In a test with 2 workers and 10 queued jobs of 0.1 s, calling it right after submitting left `started: [0, 1]` and `cancelled: 8`: the two running jobs finished, the eight queued ones never started. If running jobs must stop early, they have to check a flag themselves (an `Event`, section 7.1): Python cannot kill a thread.

### 9.5 `ProcessPoolExecutor`

The same interface, with processes, and the usual rules: guard, top-level function, picklable data. `pool.map(fn, items, chunksize=50)` sends items in batches, which saves messages when there are many small items. Section 1.2 already showed it speeding up CPU-bound work.

## 10. asyncio basics

### 10.1 Why another model?

Threads work well for tens of waits. But a chat server with 10,000 connected users would need 10,000 threads, each with its own stack, and the OS switching between them at random moments, with every shared variable a possible race.

**asyncio** takes a different approach: **one thread** runs many tasks, and the tasks switch **only at points you mark** with `await`. While a task waits for the network, it hands control back to an **event loop**, which runs whichever other task is ready. Because switches happen only at `await`, code between two `await`s can never be interrupted by another task. Many races disappear (not all; see section 13.5).

The deal is: **every waiting operation must be written to cooperate** (`await asyncio.sleep`, an async HTTP client, an async database driver). One blocking call, like `time.sleep`, freezes every task (section 14).

### 10.2 Coroutines

A function defined with `async def` is a **coroutine function**. Calling it does **not** run the body. It creates a **coroutine object**, a paused computation:

```python
import asyncio

async def greet(name):
    print(f"hello, {name}")
    return len(name)

c = greet("Asha")
print(type(c).__name__)
print("nothing printed yet")
result = asyncio.run(c)
print("result:", result)
```
```text
coroutine
nothing printed yet
hello, Asha
result: 4
```

There are two ways to run a coroutine:

- **`asyncio.run(coro)`** starts an event loop, runs the coroutine to the end, closes the loop and returns the result. It is the entry point of an async program; call it **once**, from normal (non-async) code.
- **`await coro`**, inside another `async def`, runs it and gives back its result. `await` is allowed only inside `async def`.

Forgetting `await` is the most common asyncio bug. If `main` calls `save()` without `await`, the body of `save` never runs, and Python only warns, while the program carries on:

```text
/home/you/conc/forgot.py:9: RuntimeWarning: coroutine 'save' was never awaited
  save()                 # forgot await
```

Read every `RuntimeWarning: coroutine ... was never awaited` as an error.

### 10.3 `await` alone is still sequential

```python
import asyncio
import time

async def download(name, seconds):
    print(f"start {name}")
    await asyncio.sleep(seconds)     # "waiting for the network"
    print(f"end   {name}")
    return name

async def main():
    start = time.perf_counter()
    await download("a", 0.3)
    await download("b", 0.2)
    print(f"sequential: {time.perf_counter() - start:.1f} s")

asyncio.run(main())
```
```text
start a
end   a
start b
end   b
sequential: 0.5 s
```

`await` means "run this and wait for its result **before going on**". Two awaits in a row are two steps in a row. To run things **at the same time**, you must hand several of them to the event loop together, with `asyncio.gather` or tasks:

```python
async def main():
    start = time.perf_counter()
    results = await asyncio.gather(download("a", 0.3), download("b", 0.2))
    print(results)
    print(f"concurrent: {time.perf_counter() - start:.1f} s")
```
```text
start a
start b
end   b
end   a
['a', 'b']
concurrent: 0.3 s
```

(Same `download` as before; your times will differ.) Both started, `b` finished first, and `gather` still returned results in **argument order**.

### 10.4 What the event loop does

```text
  event loop: "who is ready to run?"
     +--> run task A until an await must wait (sleep 0.3): "wake me in 0.3 s", parked
     +--> run task B until an await must wait (sleep 0.2): "wake me in 0.2 s", parked
     +--> nothing ready: sleep until the next timer or network event
     +--> 0.2 s: B is ready, run B to its end
     +--> 0.3 s: A is ready, run A to its end
```

`asyncio.sleep(seconds)` does not block anything. It tells the loop "wake me later" and gives control back. `await asyncio.sleep(0)` means "let everyone else who is ready run once, then come back to me", the asyncio version of `time.sleep(0)` in section 5.

One thread can manage a huge number of waits, because a waiting coroutine is only a small object in memory. `await asyncio.gather(*(ping(n) for n in range(10_000)))`, where each `ping` does `await asyncio.sleep(1)`, returned 10,000 results in **1.13 s** on the test machine (your times will differ). Ten thousand threads would need gigabytes of stack space.

#### Try it 10.1 (Predict the output)

```python
import asyncio

async def step(name):
    print("start", name)
    await asyncio.sleep(0.01)
    print("end", name)
    return name

async def main():
    a = step("A")
    b = step("B")
    print("made both")
    print(await b)
    print(await a)

asyncio.run(main())
```

<details><summary>Answer</summary>

```text
made both
start B
end B
B
start A
end A
A
```

Calling `step("A")` only creates a coroutine; nothing runs. Each `await` runs one coroutine to the end before the next line. `b` is awaited first, so B runs first, completely. Plain coroutines are not concurrent until you make tasks or use `gather`.

</details>

## 11. Tasks, `gather` and `TaskGroup`

### 11.1 Tasks

A **task** wraps a coroutine and schedules it on the event loop to run **in the background**. `asyncio.create_task(coro)` returns a `Task` at once; the coroutine starts the next time the current code gives control back to the loop (at an `await` that waits):

```python
import asyncio

async def worker(name):
    print(f"{name}: started")
    await asyncio.sleep(0.1)
    print(f"{name}: finished")
    return name.upper()

async def main():
    task = asyncio.create_task(worker("w1"))
    print("main: task created")
    await asyncio.sleep(0)            # first time main gives up control
    print("main: doing other work")
    result = await task
    print("main: got", result)

asyncio.run(main())
```
```text
main: task created
w1: started
main: doing other work
w1: finished
main: got W1
```

`await task` waits for it and returns its result (or re-raises its exception). A task is a kind of future: it also has `done()`, `result()`, `exception()`, `cancel()` and `cancelled()`.

Because switches happen only at `await`, the output of asyncio programs is **deterministic** when the timings are clearly different. Tasks that each `await asyncio.sleep(0)` simply take turns:

```python
import asyncio

async def count(name, n):
    for i in range(n):
        print(f"{name}{i}")
        await asyncio.sleep(0)

async def main():
    t1 = asyncio.create_task(count("a", 3))
    t2 = asyncio.create_task(count("b", 2))
    await t1
    await t2

asyncio.run(main())
```
```text
a0
b0
a1
b1
a2
```

### 11.2 Keep a reference to your tasks

The event loop keeps only a **weak** reference to tasks. A task that nobody else references can be garbage-collected before it finishes, and its work silently disappears. If you start a "fire and forget" task, keep it in a set and remove it when done:

```python
running = set()

def fire_and_forget(name):
    task = asyncio.create_task(background(name))
    running.add(task)                         # keep a strong reference
    task.add_done_callback(running.discard)   # forget it when it is done
```

Better still, use a `TaskGroup` (section 11.4), which keeps references for you and makes sure no task outlives its group.

### 11.3 `gather`

`asyncio.gather(*aws)` runs several coroutines (it wraps each in a task) and returns a list of results **in argument order**, whatever order they finish in (section 10.3). For a list, unpack it: `await asyncio.gather(*(fetch(n) for n in ids))`.

What happens when one fails? By default, `gather` raises the **first** exception as soon as it happens, but **does not cancel the others**. They keep running in the background:

```python
import asyncio

log = []

async def job(name, seconds, fail=False):
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{name} failed")
    log.append(name)
    return name

async def main():
    try:
        await asyncio.gather(job("a", 0.1), job("b", 0.05, fail=True), job("c", 0.2))
    except ValueError as e:
        print("gather raised:", e, "| finished so far:", log)
    await asyncio.sleep(0.3)
    print("later, finished:", log)

    results = await asyncio.gather(job("x", 0.05), job("y", 0.01, fail=True),
                                   return_exceptions=True)
    print(results)

asyncio.run(main())
```
```text
gather raised: b failed | finished so far: []
later, finished: ['a', 'c']
['x', ValueError('y failed')]
```

With `return_exceptions=True`, exceptions are **returned in the result list** instead of raised. That is perfect for "try everything and report which ones failed": check each item with `isinstance(r, Exception)`.

### 11.4 `TaskGroup`: all or nothing

`asyncio.TaskGroup` (Python 3.11+) is the modern, safer tool. Tasks are created inside an `async with` block, and the block **does not end until every task has finished**. If any task fails, the group **cancels all the others**, waits for them, and raises an **`ExceptionGroup`** containing the error(s):

```python
import asyncio

log = []

async def job(name, seconds, fail=False):
    try:
        await asyncio.sleep(seconds)
        if fail:
            raise ValueError(f"{name} failed")
        log.append(f"{name} ok")
        return name
    except asyncio.CancelledError:
        log.append(f"{name} cancelled")
        raise

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            ta = tg.create_task(job("a", 0.1))
            tb = tg.create_task(job("b", 0.05, fail=True))
            tc = tg.create_task(job("c", 0.2))
    except* ValueError as group:
        print("caught:", group.exceptions)
    print(log)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(job(n, 0.01)) for n in "xyz"]
    print([t.result() for t in tasks])

asyncio.run(main())
```
```text
caught: (ValueError('b failed'),)
['c cancelled', 'a cancelled']
['x', 'y', 'z']
```

Compare with `gather`: there, `a` and `c` kept running after `b` failed; here they were cancelled. After a successful group, every task is done, so `t.result()` is safe.

`except*` (Python 3.11+) is the way to catch from an `ExceptionGroup`: each `except*` clause takes the matching exceptions out of the group, and **several clauses can run**, since several tasks can fail with different errors. A group whose two tasks raised `ValueError("bad value")` and `KeyError("missing")`, caught by `except* ValueError as eg:` and `except* KeyError as eg:`, ran **both** clauses: `eg.exceptions` was `(ValueError('bad value'),)` in the first and `(KeyError('missing'),)` in the second. A plain `except ValueError:` would **not** catch an `ExceptionGroup` at all.

**Which to use?**

| You want... | Use |
|---|---|
| all results; any failure means the whole job failed | `TaskGroup` |
| every result, with failures reported one by one | `gather(..., return_exceptions=True)` |
| results in input order with simple code, failures rare | `gather` (but remember the others keep running) |

#### Try it 11.1 (Predict the output)

```python
import asyncio

async def job(name, delay):
    print(name, "begin")
    await asyncio.sleep(delay)
    print(name, "end")

async def main():
    t1 = asyncio.create_task(job("A", 0.2))
    t2 = asyncio.create_task(job("B", 0.1))
    print("tasks created")
    await job("C", 0.15)
    await t1
    print("main end")

asyncio.run(main())
```

<details><summary>Answer</summary>

```text
tasks created
C begin
A begin
B begin
B end
C end
A end
main end
```

Creating tasks does not run them. `await job("C", 0.15)` runs C's body directly in `main` (a plain coroutine, not a task), so "C begin" prints before the loop gets a chance to start A and B. When C sleeps, A and B start. Then they finish by their sleep times: B at 0.1, C at 0.15, A at 0.2. Note that `t2` is never awaited, but it still ran, because it is a task.

</details>

## 12. Timeouts and cancellation

### 12.1 Never wait forever

A server that never answers, a lock nobody releases, a queue nobody fills: real programs need **deadlines**. In asyncio, use `asyncio.timeout` (3.11+) as an `async with` block. If the block is still running when time is up, the code inside is **cancelled**, and `TimeoutError` is raised at the block:

```python
import asyncio

async def slow_report():
    await asyncio.sleep(1)
    return "report"

async def main():
    try:
        async with asyncio.timeout(0.2):
            print(await slow_report())
    except TimeoutError:
        print("gave up after 0.2 s")

    try:
        print(await asyncio.wait_for(slow_report(), timeout=0.2))
    except TimeoutError:
        print("wait_for also gave up")

    async with asyncio.timeout(2):
        print(await slow_report())

asyncio.run(main())
```
```text
gave up after 0.2 s
wait_for also gave up
report
```

`asyncio.wait_for(aw, timeout)` is the older one-call form. `asyncio.timeout` is more flexible, because one deadline can cover **several** awaits (a "total" deadline). Use `asyncio.timeout(None)` for "no deadline" and `asyncio.timeout_at(loop.time() + n)` for an absolute deadline.

### 12.2 How cancellation works

`task.cancel()` does not kill anything instantly. It **asks** the task to stop: the next time the task is at an `await`, a **`CancelledError`** is raised inside it, at that `await`. The exception unwinds the task's code like any other, so `finally` blocks and `async with` exits **run**. That is what makes clean-up possible:

```python
import asyncio

async def worker():
    print("worker: opening file")
    try:
        await asyncio.sleep(10)
        print("worker: never gets here")
    finally:
        print("worker: closing file (finally runs)")

async def main():
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("main: task was cancelled")
    print("task.cancelled():", task.cancelled())

asyncio.run(main())
```
```text
worker: opening file
worker: closing file (finally runs)
main: task was cancelled
task.cancelled(): True
```

Awaiting a cancelled task raises `CancelledError` in the waiter too. Timeouts are built on cancellation: `asyncio.timeout` cancels the inner code, then turns the `CancelledError` into `TimeoutError` at the edge of the block.

### 12.3 Never swallow `CancelledError`

`CancelledError` is a subclass of `BaseException`, **not** `Exception`, so `except Exception:` does not catch it. That is on purpose: cancellation should pass through ordinary error handling. If you catch it explicitly to clean up, you **must re-raise it**:

```python
import asyncio

async def stubborn():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("stubborn: ignoring cancel")      # BAD: swallowed
    return "pretended to finish"

async def polite():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("polite: cleaning up")
        raise                                   # GOOD: re-raise

async def main():
    for coro_fn in (stubborn, polite):
        task = asyncio.create_task(coro_fn())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            print("result:", await task)
        except asyncio.CancelledError:
            pass
        print(coro_fn.__name__, "cancelled():", task.cancelled())

asyncio.run(main())
```
```text
stubborn: ignoring cancel
result: pretended to finish
stubborn cancelled(): False
polite: cleaning up
polite cancelled(): True
```

Swallowing it breaks everything built on cancellation. Even `asyncio.timeout` stops working: a task that catches the `CancelledError` and returns a value makes the `async with asyncio.timeout(0.1):` block finish normally, with no `TimeoutError` at all. The same applies to `TaskGroup` and shutdown code: a task that swallows cancellation can make the program hang at exit. Rule: **clean up in `finally`; if you must `except CancelledError`, end with `raise`.**

### 12.4 `asyncio.wait` and `as_completed`

`asyncio.wait(tasks, timeout=..., return_when=...)` works like `concurrent.futures.wait`: it returns `(done, pending)` sets and does **not** cancel anything by itself. Whatever is pending is your job:

```python
import asyncio

async def job(name, seconds):
    await asyncio.sleep(seconds)
    return name

async def main():
    tasks = [asyncio.create_task(job(n, s)) for n, s in [("a", 0.3), ("b", 0.1), ("c", 0.5)]]
    done, pending = await asyncio.wait(tasks, timeout=0.2)
    print("done:", [t.result() for t in done])
    print("pending:", len(pending))
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)   # let them finish cancelling
    print("all cancelled:", all(t.cancelled() for t in pending))

asyncio.run(main())
```
```text
done: ['b']
pending: 2
all cancelled: True
```

Two habits are shown here. First, **cancel *and* await** the leftovers: `cancel()` only asks; awaiting them (with `return_exceptions=True` so their `CancelledError` does not stop you) lets their `finally` blocks run before you continue. Second, for results in completion order there is `asyncio.as_completed`: with `job("x", 0.2)` and `job("y", 0.1)`, `async for t in asyncio.as_completed([...]): print(await t)` printed `y` then `x`. (`async for` works from Python 3.13; on 3.11–3.12 write `for t in asyncio.as_completed(...): r = await t`.)

### 12.5 `shield` (briefly)

`await asyncio.shield(aw)` protects an inner operation from the cancellation of the code that awaits it: the outer task is cancelled, but the inner one keeps running. In a test, a handler doing `await asyncio.shield(save_to_disk())` (a 0.2 s save) was cancelled after 0.05 s; at that moment nothing was saved, but 0.3 s later the save had completed. Use it rarely, for short operations that must not be left half-done. A shielded operation can still be lost if the whole program ends before it finishes.

#### Try it 12.1 (Predict the output)

```python
import asyncio

async def worker():
    try:
        print("worker: start")
        await asyncio.sleep(1)
        print("worker: end")
    except asyncio.CancelledError:
        print("worker: cancelled")
        raise
    finally:
        print("worker: finally")

async def main():
    try:
        async with asyncio.timeout(0.1):
            await worker()
    except TimeoutError:
        print("main: TimeoutError")

asyncio.run(main())
```

<details><summary>Answer</summary>

```text
worker: start
worker: cancelled
worker: finally
main: TimeoutError
```

After 0.1 s the timeout cancels the code inside the block: `CancelledError` is raised at `await asyncio.sleep(1)`. The `except` prints and re-raises, `finally` runs, and at the edge of the `async with` the cancellation becomes `TimeoutError`. If the `except` did not re-raise, there would be no `TimeoutError` (section 12.3).

</details>

## 13. Bounded concurrency and shared state in asyncio

### 13.1 Why limit?

`gather` over 10,000 URLs starts 10,000 requests **at once**. The server sees an attack and blocks you, your machine runs out of sockets, and nothing finishes faster. Real programs need a limit: "at most 10 requests in flight".

### 13.2 `asyncio.Semaphore`

The same idea as `threading.Semaphore` (section 7.2), but with `async with`:

```python
import asyncio
import time

in_flight = 0
peak = 0

async def fetch(n, sem):
    global in_flight, peak
    async with sem:
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.1)
        in_flight -= 1
        return n * n

async def main():
    sem = asyncio.Semaphore(3)
    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(n, sem) for n in range(10)))
    print(results)
    print("peak in flight:", peak)
    print(f"took {time.perf_counter() - start:.1f} s")

asyncio.run(main())
```
```text
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
peak in flight: 3
took 0.4 s
```

No lock is needed around `in_flight += 1`: there is no `await` between reading and writing it, so no other task can run in between. Create the semaphore **inside** the running program (in `main`), not at module level, so it belongs to the right event loop.

A semaphore still creates all 10,000 coroutines up front; they just wait their turn. That is fine for thousands of small items.

### 13.3 A worker pool with `asyncio.Queue`

For very many items, or a stream of items that arrive over time, start a **fixed number of workers** that pull from an `asyncio.Queue`. It is the async version of section 7.5:

```python
import asyncio

async def work(item):
    await asyncio.sleep(0.05 * (item % 3))
    if item == 4:
        raise ValueError("item 4 is broken")
    return item * 10

async def worker(name, queue, results, errors):
    while True:
        index, item = await queue.get()
        try:
            results[index] = await work(item)
        except Exception as e:
            errors.append((index, e))
        finally:
            queue.task_done()

async def main():
    items = [1, 2, 3, 4, 5, 6]
    queue = asyncio.Queue()
    for pair in enumerate(items):
        queue.put_nowait(pair)
    results = [None] * len(items)
    errors = []
    workers = [asyncio.create_task(worker(f"w{i}", queue, results, errors)) for i in range(3)]
    await queue.join()                 # every item processed
    for w in workers:
        w.cancel()                     # workers loop forever: stop them
    await asyncio.gather(*workers, return_exceptions=True)
    print(results)
    print(errors)

asyncio.run(main())
```
```text
[10, 20, 30, None, 50, 60]
[(3, ValueError('item 4 is broken'))]
```

The pieces: items carry their **index**, so results land in input order. Each worker catches errors **per item**: one bad item must not kill the worker, or the remaining items would never be processed and `queue.join()` would wait forever. `task_done()` is in `finally`, so it runs even on error. After `join()`, the workers are stuck in `await queue.get()`: cancel them and **await** them (sentinels, one per worker, work too).

### 13.4 Backpressure with a bounded queue

`asyncio.Queue(maxsize=n)` makes `await queue.put(...)` **wait** while the queue is full. A fast producer is held back to the speed of the slow consumer, so memory stays small:

```python
import asyncio

log = []

async def producer(queue):
    for n in range(5):
        await queue.put(n)            # waits while the queue is full
        log.append(f"put {n} (size {queue.qsize()})")
    await queue.put(None)

async def consumer(queue):
    while (item := await queue.get()) is not None:
        await asyncio.sleep(0.1)      # slow consumer
        log.append(f"     got {item}")

async def main():
    queue = asyncio.Queue(maxsize=2)
    await asyncio.gather(producer(queue), consumer(queue))
    print("\n".join(log))

asyncio.run(main())
```
```text
put 0 (size 1)
put 1 (size 2)
put 2 (size 2)
     got 0
put 3 (size 2)
     got 1
put 4 (size 2)
     got 2
     got 3
     got 4
```

The size never goes above 2. After the first few items, every `put` has to wait for a `got`.

### 13.5 Races still exist in asyncio

"One thread, so no races" is only half true. Code **between** two awaits cannot be interrupted, but any `await` is a place where other tasks run. A check-then-act with an `await` in the middle is a race:

```python
import asyncio

class Wallet:
    def __init__(self, balance):
        self.balance = balance
        self.lock = asyncio.Lock()

    async def spend_unsafe(self, amount):
        if self.balance >= amount:          # check
            await asyncio.sleep(0.01)       # e.g. ask the bank: other tasks run here
            self.balance -= amount          # act
            return True
        return False

    async def spend_safe(self, amount):
        async with self.lock:
            return await self.spend_unsafe(amount)

async def main():
    w = Wallet(100)
    print(await asyncio.gather(*(w.spend_unsafe(60) for _ in range(3))), w.balance)
    w = Wallet(100)
    print(await asyncio.gather(*(w.spend_safe(60) for _ in range(3))), w.balance)

asyncio.run(main())
```
```text
[True, True, True] -80
[True, False, False] 40
```

`asyncio.Lock` is used with `async with`, and waiting for it lets other tasks run. Never use a `threading.Lock` in async code: waiting for it blocks the whole event loop. asyncio also has `Event`, `Condition` and `Barrier`, with the same ideas as the threading versions and `await` on their waits.

#### Try it 13.1

`gather` over 100 coroutines, each wrapped in `async with sem:` where `sem = asyncio.Semaphore(5)`, and each awaiting `asyncio.sleep(0.1)`. (a) About how long does it take? (b) Someone creates the semaphore with `asyncio.Semaphore(5)` **inside** each coroutine instead of once outside. What happens?

<details><summary>Answer</summary>

(a) 100 / 5 = 20 waves of 0.1 s, about **2 s**. (b) Every coroutine gets its own semaphore with 5 free slots, so nothing is limited: all 100 run at once and the run takes about 0.1 s. A limit only works if every task shares **the same** semaphore object.

</details>

## 14. Blocking calls inside async code

### 14.1 One blocking call freezes everything

The event loop runs on one thread. If a coroutine calls a function that **blocks** (does not give control back), every other task waits:

```python
import asyncio
import time

async def bad(name):
    print(f"start {name}")
    time.sleep(0.2)              # blocks the WHOLE loop
    print(f"end   {name}")

async def main():
    start = time.perf_counter()
    await asyncio.gather(bad("a"), bad("b"))
    print(f"took {time.perf_counter() - start:.1f} s")

asyncio.run(main())
```
```text
start a
end   a
start b
end   b
took 0.4 s
```

No overlap at all. Typical blocking calls hiding in async code: `time.sleep`, `requests.get` (a sync HTTP library), sync database drivers (`sqlite3`, `psycopg2`), reading big files, `subprocess.run`, and long CPU work (`sum(range(10**8))`, parsing a huge JSON). The rule of thumb: **inside `async def`, anything that waits must be awaited, and anything slow must be moved off the loop.**

### 14.2 `asyncio.to_thread`

`await asyncio.to_thread(func, *args)` runs a blocking function in a worker thread and lets the loop keep running meanwhile. This test runs four blocking lookups while a heartbeat task tries to tick every 0.05 s:

```python
import asyncio
import time

def blocking_lookup(n):
    time.sleep(0.2)              # e.g. an old database driver
    return n * 2

async def heartbeat(stop):
    beats = 0
    while not stop.is_set():
        beats += 1
        await asyncio.sleep(0.05)
    return beats

async def main(offload):
    stop = asyncio.Event()
    hb = asyncio.create_task(heartbeat(stop))
    start = time.perf_counter()
    if offload:
        results = await asyncio.gather(*(asyncio.to_thread(blocking_lookup, n) for n in range(4)))
    else:
        results = [blocking_lookup(n) for n in range(4)]
    elapsed = time.perf_counter() - start
    stop.set()
    print(f"offload={offload}: {results} in {elapsed:.1f} s, heartbeats={await hb}")

asyncio.run(main(offload=False))
asyncio.run(main(offload=True))
```
```text
offload=False: [0, 2, 4, 6] in 0.8 s, heartbeats=0
offload=True: [0, 2, 4, 6] in 0.2 s, heartbeats=5
```

(Your times and heartbeat counts will differ a little.) Blocking directly: 0.8 s and the heartbeat **never ran**. Offloaded: the four lookups overlapped in threads, and the loop stayed alive. A heartbeat counter like this is how tests check that the loop is not blocked.

### 14.3 `run_in_executor` for CPU work

`to_thread` uses threads, which do not help CPU-bound work (the GIL). For that, send the work to a **process pool** with `loop.run_in_executor(executor, func, *args)`, which returns an awaitable:

```python
async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = await asyncio.gather(
            loop.run_in_executor(pool, count_primes, 10_000),
            loop.run_in_executor(pool, count_primes, 20_000),
        )
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```
```text
[1229, 2262]
```

(`count_primes` is a top-level function like the one in section 1.2.) `run_in_executor(None, ...)` uses the loop's default thread pool, which is what `to_thread` does for you. `run_in_executor` takes only positional arguments; for keyword arguments wrap the call with `functools.partial`.

### 14.4 Finding blocking calls: debug mode

asyncio has a **debug mode** that warns when one step of a task holds the loop for more than 0.1 s. Turn it on with `asyncio.run(main(), debug=True)`, the environment variable `PYTHONASYNCIODEBUG=1`, or `python -X dev`:

```python
import asyncio
import time

async def handler():
    time.sleep(0.3)              # a blocking call hiding in async code

asyncio.run(handler(), debug=True)
```
```text
Executing <Task finished name='Task-1' coro=<handler() done, defined at /home/you/conc/debug.py:4> result=None created at /usr/lib/python3.14/asyncio/runners.py:109> took 0.301 seconds
```

It names the coroutine that held the loop, and how long. Debug mode also reports coroutines that were never awaited and tasks that were destroyed while still pending. Use it in development, not in production (it slows things down).

#### Try it 14.1

Inside an `async def` handler, which of these block the event loop? For each blocking one, name the fix.

1. `time.sleep(1)`
2. `await asyncio.sleep(1)`
3. `requests.get(url)` (the sync `requests` library)
4. `await client.get(url)` with an `httpx.AsyncClient`
5. `hashlib.sha256(ten_gigabytes).hexdigest()`
6. `json.loads(small_string)` (a few hundred bytes)

<details><summary>Answer</summary>

1. Blocks. Use `await asyncio.sleep(1)`.
2. Does not block.
3. Blocks. Use an async client (`httpx.AsyncClient`), or `await asyncio.to_thread(requests.get, url)`.
4. Does not block.
5. Blocks for a long time (CPU work). Use `await loop.run_in_executor(process_pool, ...)`; `to_thread` would also free the loop here, because `hashlib` releases the GIL on big inputs.
6. Technically runs on the loop, but it takes microseconds. Short CPU work is fine; only *slow* work needs moving.

</details>

## 15. Async iterators, generators and context managers

### 15.1 `async for` and async iterators

A normal `for` loop calls `__next__` and cannot wait. When getting each item requires waiting (the next message from a socket, the next page of an API), use `async for`, which calls **`__anext__`**, an `async` method, and stops on **`StopAsyncIteration`**:

```python
import asyncio

class Countdown:
    def __init__(self, start):
        self.current = start

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current <= 0:
            raise StopAsyncIteration
        await asyncio.sleep(0.01)     # e.g. waiting for the next message
        self.current -= 1
        return self.current + 1
```

Inside an `async def`, `async for n in Countdown(3): print(n)` prints `3`, `2`, `1`.

### 15.2 Async generators

Writing the class is rarely needed. An `async def` that contains `yield` is an **async generator**: it can `await` between yields. It is the cleanest way to hide pagination:

```python
import asyncio

PAGES = {1: ["a", "b"], 2: ["c"], 3: []}

async def fetch_page(n):
    print(f"  (fetching page {n})")
    await asyncio.sleep(0.01)
    return PAGES.get(n, [])

async def all_items():
    page = 1
    while True:
        items = await fetch_page(page)
        if not items:
            return
        for item in items:
            yield item
        page += 1

async def main():
    async for item in all_items():
        print(item)

asyncio.run(main())
```
```text
  (fetching page 1)
a
b
  (fetching page 2)
c
  (fetching page 3)
```

Pages are fetched **lazily**: page 2 is requested only when the consumer wants the item after `b`. `[x async for x in all_items()]` is an async comprehension (allowed inside `async def`); it gives `['a', 'b', 'c']`.

### 15.3 Closing early: `aclose()`

If the consumer stops early (`break`), the generator is paused at a `yield`, and its `finally` has not run. With a normal generator, Python closes it quickly when it is garbage-collected. An async generator's clean-up needs the event loop, so it may run late or only at loop shutdown. Close it yourself with `await gen.aclose()`, which raises `GeneratorExit` at the paused `yield` and runs the `finally` **now** (Try it 15.1 shows the order). `contextlib.aclosing(gen)` does the same as an `async with` block: `async with aclosing(lines()) as gen: async for line in gen: ...`. This matters when the generator holds a connection or a file.

### 15.4 Async context managers

`async with` calls **`__aenter__`** and **`__aexit__`**, which are coroutines, so opening and closing can await (a network handshake, flushing a buffer). `__aexit__(self, exc_type, exc, tb)` runs even when the body raises, and returning `False` lets the error continue. The quicker way, as with normal context managers, is a decorator: `@asynccontextmanager` turns an async generator with one `yield` into a context manager:

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def opened(name, log):
    await asyncio.sleep(0)
    log.append(f"open {name}")
    try:
        yield name.upper()
    finally:
        log.append(f"close {name}")

async def main():
    log = []
    async with opened("db", log) as handle:
        log.append(f"use {handle}")
    try:
        async with opened("cache", log):
            raise RuntimeError("boom")
    except RuntimeError:
        log.append("caught boom")
    print(log)

asyncio.run(main())
```
```text
['open db', 'use DB', 'close db', 'open cache', 'close cache', 'caught boom']
```

The `try/finally` around `yield` is what makes the close happen on error; without it, an exception in the body would skip the clean-up line.

#### Try it 15.1 (Predict the output)

```python
import asyncio

async def numbers():
    try:
        for n in range(5):
            yield n
            print("resumed after", n)
    finally:
        print("generator closed")

async def main():
    gen = numbers()
    async for n in gen:
        print("got", n)
        if n == 1:
            break
    await gen.aclose()
    print("done")

asyncio.run(main())
```

<details><summary>Answer</summary>

```text
got 0
resumed after 0
got 1
generator closed
done
```

After `got 1` the loop breaks while the generator is paused at `yield 1`, so "resumed after 1" never prints. `aclose()` raises `GeneratorExit` at that `yield`, and the `finally` runs before "done".

</details>

## 16. `httpx` for async HTTP

### 16.1 Why httpx

The popular `requests` library is synchronous: it blocks the event loop (section 14). **httpx** has almost the same interface as `requests` and adds an async client, `httpx.AsyncClient`, whose methods are awaited. It also has a built-in way to fake a server for tests, which this section uses for every example: **`httpx.MockTransport`**. A transport is the part of the client that actually sends bytes; a mock transport instead calls **your function** with the request and returns whatever response you build. No network, no flaky tests.

```python
import asyncio
import httpx

def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Asha"})
    return httpx.Response(404, text="not found")

async def main():
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.example.com") as client:
        r = await client.get("/users/1")
        print(r.status_code, r.json())

        r = await client.get("/users/99")
        print(r.status_code, r.text)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("HTTPStatusError:", e.response.status_code)

asyncio.run(main())
```
```text
200 {'id': 1, 'name': 'Asha'}
404 not found
HTTPStatusError: 404
```

In real code you would write `httpx.AsyncClient(base_url=...)` without the `transport`; nothing else changes. That is why functions should **take the client as a parameter**: the program passes a real client, the tests pass one with a mock transport.

Key points:

- **Create one client and reuse it** for all requests. A client keeps a pool of open connections; making a new client per request throws that away and is much slower. `async with` closes it at the end.
- A response with status 404 or 500 is **not** an exception by itself. Call `r.raise_for_status()` to turn 4xx/5xx into `httpx.HTTPStatusError`.
- `r.json()`, `r.text`, `r.content` (bytes), `r.headers`, `r.status_code` read the response. `params={"page": 2}`, `json={...}` and `headers={...}` build requests.

### 16.2 Errors

httpx errors come in two families:

```python
import asyncio
import httpx

def handler(request):
    if request.url.host == "down.example.com":
        raise httpx.ConnectError("connection refused", request=request)
    return httpx.Response(503)

async def main():
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        for url in ["https://down.example.com/", "https://busy.example.com/"]:
            try:
                r = await client.get(url)
                r.raise_for_status()
            except httpx.TransportError as e:
                print("transport problem:", type(e).__name__, "-", e)
            except httpx.HTTPStatusError as e:
                print("server said:", e.response.status_code, e.response.reason_phrase)

asyncio.run(main())
```
```text
transport problem: ConnectError - connection refused
server said: 503 Service Unavailable
```

- **`httpx.TransportError`**: the request never got a proper answer: could not connect, connection dropped, timed out (`ConnectError`, `ReadError`, `ConnectTimeout`, `ReadTimeout`, ... are all subclasses). Often worth **retrying**.
- **`httpx.HTTPStatusError`** (from `raise_for_status`, **not** a `TransportError`): the server answered with an error code. **5xx** (server trouble, 503 busy) is often worth retrying; **4xx** (your request is wrong: 404 not found, 401 not allowed) is not, since asking again will get the same answer.

Both inherit from `httpx.HTTPError`, if you want to catch everything from httpx.

### 16.3 Timeouts

httpx has timeouts **on by default** (5 seconds) for each phase: connecting, reading, writing, waiting for a pooled connection. You can change them per client or per request:

`httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0))` gives a client whose `client.timeout` prints as `Timeout(connect=3.0, read=10.0, write=10.0, pool=10.0)`.

These are **per-phase** limits. A server that sends one byte every 9 seconds never trips a 10-second read timeout, and a download could take hours. For a real **deadline** on a whole request (or a whole batch), wrap it in `asyncio.timeout` (section 12):

```python
try:
    async with asyncio.timeout(0.2):
        await client.get("https://slow.example.com/")
except TimeoutError:
    print("gave up after 0.2 s")
```

With a mock handler that does `await asyncio.sleep(5)` before answering, this printed `gave up after 0.2 s`.

(Note: a mock transport ignores httpx's own timeout settings, because no real socket is involved. In tests, always use `asyncio.timeout` for deadlines.)

### 16.4 Many requests with a limit

Everything from sections 11–13 combines naturally: **one** client, **one** semaphore, `gather`. To prove the limit in a test, make the mock handler `async` and count requests in flight, exactly like the peak counter in section 13.2:

```python
async def handler(request):
    global in_flight, peak
    in_flight += 1
    peak = max(peak, in_flight)
    await asyncio.sleep(0.1)                 # a slow server
    in_flight -= 1
    return httpx.Response(200, text=f"page {request.url.path}")

async def fetch(client, sem, url):
    async with sem:
        r = await client.get(url)
        return url, r.status_code
```

Fetching 12 URLs with `asyncio.Semaphore(4)` gave 12 results, all 200, a **peak in flight of 4**, in 0.3 s (three waves; your times will differ).

### 16.5 Retries with exponential backoff

Networks fail now and then. A **retry** asks again; **backoff** waits longer after each failure (0.5 s, 1 s, 2 s, ...: `base * 2 ** attempt`), so a struggling server gets time to recover. Retry only what can succeed next time (transport errors, 5xx), never 4xx. And make the waiting **injectable**: a `sleep` parameter that defaults to `asyncio.sleep`, so tests can pass a fake that records delays instead of waiting:

```python
import asyncio
import httpx

answers = iter([503, 502, 200])

def handler(request):
    return httpx.Response(next(answers), text="hello")

async def get_with_retry(client, url, retries=3, base_delay=0.5, sleep=asyncio.sleep):
    for attempt in range(retries + 1):
        try:
            r = await client.get(url)
            if r.status_code < 500:
                r.raise_for_status()         # 4xx: our fault, do not retry
                return r
            error = httpx.HTTPStatusError(f"server error {r.status_code}",
                                          request=r.request, response=r)
        except httpx.TransportError as e:
            error = e
        if attempt == retries:
            raise error
        delay = base_delay * 2 ** attempt
        print(f"attempt {attempt + 1} failed ({error}); waiting {delay} s")
        await sleep(delay)

async def main():
    waited = []

    async def fake_sleep(seconds):           # record instead of waiting
        waited.append(seconds)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        r = await get_with_retry(client, "https://flaky.example.com/", sleep=fake_sleep)
    print("final:", r.status_code, r.text, "| waited:", waited)

asyncio.run(main())
```
```text
attempt 1 failed (server error 503); waiting 0.5 s
attempt 2 failed (server error 502); waiting 1.0 s
final: 200 hello | waited: [0.5, 1.0]
```

The test finished instantly, yet it checked the exact delays. In production, add a little randomness ("jitter", e.g. `delay * random.uniform(0.5, 1.5)`) so that a thousand clients that failed together do not all retry at the same instant.

### 16.6 Streaming big responses

`await client.get(url)` reads the whole body into memory. For big files, stream it in chunks:

```python
async with client.stream("GET", "https://files.example.com/big.bin") as r:
    r.raise_for_status()
    async for chunk in r.aiter_bytes(chunk_size=4096):
        f.write(chunk)
```

With a mock handler returning 10,000 bytes, the loop received 3 chunks (4,096 + 4,096 + 1,808 bytes). The module project uses this to write a download to disk piece by piece.

#### Try it 16.1

A function `fetch_status(client, url)` works in production. Your test builds `httpx.AsyncClient(transport=httpx.MockTransport(handler))` with a plain `def handler(request)` that returns `httpx.Response(503)`. (a) Does `await client.get(url)` raise? (b) How would you make the handler slow, to test a timeout? (c) Why does the function take `client` as a parameter instead of creating one inside?

<details><summary>Answer</summary>

(a) No. A 503 is a normal response; only `r.raise_for_status()` turns it into `httpx.HTTPStatusError`. (b) Make the handler `async def` and `await asyncio.sleep(...)` inside it, then wrap the call in `asyncio.timeout(...)` (the mock transport ignores httpx's own timeouts). (c) So the caller decides which client to use: a real one in production, a mock one in tests. It also lets one client, with its connection pool, be reused for every request.

</details>

## 17. Choosing the right tool

### 17.1 The decision

Start with the question from section 1: **is the program waiting or computing?**

```text
                       Is it slow because it WAITS or because it COMPUTES?
                              /                               \
                          waits                             computes
                           /                                    \
         How many things at once?                    Is the hot loop in pure Python?
           /                 \                          /                    \
   a few to a hundred     thousands, or the        yes: processes           no, in C that releases
   (or a sync library)    libraries are async      (ProcessPoolExecutor)    the GIL (NumPy, hashlib):
          |                      |                                          threads may be enough
       threads                asyncio
 (ThreadPoolExecutor)    (+ httpx, async drivers)
```

| Situation | Best fit | Why not the others |
|---|---|---|
| Download 200 pages with `requests` | `ThreadPoolExecutor(max_workers=10)` | asyncio needs an async HTTP library; processes are heavy for waiting |
| Crawl 50,000 pages | asyncio + `httpx.AsyncClient` + semaphore | 50,000 threads are too many; processes do not help waiting |
| Resize 5,000 images | `ProcessPoolExecutor` | the GIL stops threads; asyncio is one thread |
| Chat server, thousands of idle connections | asyncio | one task per connection is cheap; one thread each is not |
| Run a slow sync database call inside an async web app | `asyncio.to_thread` | blocking the loop freezes every user |
| Parse 100 big CSV files, then upload results | processes for parsing, asyncio (or threads) for uploading | each part has its own bottleneck |
| A script that runs once a night in 3 minutes | nothing: keep it simple | complexity costs more than it saves |

### 17.2 Mixing models

Real programs often mix them, and the tools are designed for it. Whatever you mix, the same rules hold: bound the concurrency, give everything a deadline, decide what happens on failure, and clean up on cancellation.

- **asyncio + threads**: `asyncio.to_thread` for blocking libraries (section 14.2).
- **asyncio + processes**: `loop.run_in_executor(process_pool, fn, ...)` for CPU work (section 14.3). A common design is an async program that downloads with httpx and hands each downloaded file to a process pool for heavy parsing.
- **threads + asyncio**: a sync program can run one coroutine with `asyncio.run`; a thread that must hand work to a running loop uses `asyncio.run_coroutine_threadsafe(coro, loop)`.

#### Try it 17.1

A teammate wants to speed up a script that reads 40 local text files (a few MB each) and counts the words in each with a pure-Python loop. It takes 30 s and `htop` shows one core at 100%. They propose `asyncio.gather` with `aiofiles`. What do you tell them?

<details><summary>Answer</summary>

The script is **CPU-bound** (one core at 100%, the time is in the word-counting loop, not in reading). asyncio runs on one thread, so it cannot make computation faster, and async file reading only helps waiting, which is a tiny part here. Use a `ProcessPoolExecutor`, passing **file names** (not file contents) to a top-level `count_words(path)` function, under an `if __name__ == "__main__":` guard. Measure before and after; with 8 cores expect a few times faster, not 8 times.

</details>

## 18. Module project: a concurrent downloader

The module project (problem p050) brings the whole chapter together. You will build:

```python
async def download_all(client, urls, dest, *, limit=4, retries=2, timeout=2.0,
                       sleep=asyncio.sleep) -> dict:
    ...
```

It downloads every URL with the given `httpx.AsyncClient`, saves each body to `dest/<name>` (the last part of the URL path), and returns a report mapping each URL to `"ok"`, `"failed: <reason>"` or `"timeout"`. This section walks through the **design**; writing the code is your job.

### 18.1 Requirements, and the tool for each

| Requirement | Tool from this chapter |
|---|---|
| Many downloads overlap | tasks / `gather` / `TaskGroup` (section 11) |
| At most `limit` in flight | `asyncio.Semaphore(limit)` (section 13.2) |
| Retry 5xx and transport errors, not 4xx, with backoff | the retry loop of section 16.5, with the injected `sleep` |
| Each download has a deadline | `asyncio.timeout(timeout)` (section 12.1) |
| One bad URL does not stop the others | catch per URL and put the reason in the report (like `return_exceptions`) |
| No half-written files, ever | a `.part` file renamed on success (below) |
| Cancelling the whole call leaves nothing behind | `finally` clean-up; never swallow `CancelledError` (section 12.3) |

### 18.2 Structure

Split the work into small functions, each with one job:

```text
download_all(client, urls, dest, ...)
    make one Semaphore(limit)
    run download_one(url) for every url concurrently, collect the reports
    return {url: report}

download_one(url)                       -> "ok" | "failed: ..." | "timeout"
    async with semaphore:               (the limit covers retries too)
        for each attempt:
            try:
                async with asyncio.timeout(timeout):
                    fetch_to_file(url, dest / name)
                return "ok"
            except timeout          -> "timeout"   (retry or not: your decision, documented)
            except 4xx              -> "failed: 404" (no retry)
            except 5xx / transport  -> wait base * 2**attempt with sleep(), try again
        after the last attempt      -> "failed: <reason>"

fetch_to_file(url, final_path)
    write into final_path + ".part", rename on success, delete the .part on any failure
```

Questions to decide before coding (and to write in a docstring): does the `timeout` cover one attempt or all attempts of one URL? Is a timeout retried? What is the "reason" text for a transport error (the exception class name is a good choice)? The tests in p050 tell you what they expect; read them first.

### 18.3 Safe files: write to `.part`, then rename

If a download fails half-way, a half-written `photo.jpg` looks like a real file, and the next run might skip it. The safe pattern: write to `photo.jpg.part`, and only when every byte is written, **rename** it to `photo.jpg` with `os.replace`. A rename within one folder is atomic: other programs see either no file or the complete file. On any failure, including cancellation, delete the `.part` in a `finally` block. Here is the pattern on its own, with a fake chunk source instead of httpx:

```python
import asyncio
import os
import tempfile
from pathlib import Path

async def save_chunks(chunks, final: Path):
    part = final.with_name(final.name + ".part")
    try:
        with open(part, "wb") as f:
            for chunk in chunks:
                await asyncio.sleep(0.05)       # waiting for the next chunk
                f.write(chunk)
        os.replace(part, final)                 # atomic: all or nothing
    finally:
        part.unlink(missing_ok=True)            # gone after error or cancel

async def main():
    folder = Path(tempfile.mkdtemp())
    await save_chunks([b"abc", b"def"], folder / "ok.txt")

    task = asyncio.create_task(save_chunks([b"x"] * 10, folder / "big.bin"))
    await asyncio.sleep(0.12)
    print("while running:", sorted(p.name for p in folder.iterdir()))
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("after cancel: ", sorted(p.name for p in folder.iterdir()))
    print("ok.txt holds:", (folder / "ok.txt").read_bytes())

asyncio.run(main())
```
```text
while running: ['big.bin.part', 'ok.txt']
after cancel:  ['ok.txt']
ok.txt holds: b'abcdef'
```

After a successful `os.replace`, the `.part` no longer exists, so `unlink(missing_ok=True)` in `finally` does nothing. After a cancel, it removes the partial file, and the `CancelledError` keeps travelling up. In the project, the chunks come from `client.stream(...)` and `aiter_bytes()` (section 16.6), and you call `raise_for_status()` **before** opening the file, so an error page is never saved.

### 18.4 How it will be tested

The p050 tests use everything you have seen in this chapter's examples: a `MockTransport` whose async handler counts **in-flight requests** (peak must not exceed `limit`), returns 503 a few times before succeeding (to check retries and the delays recorded by a fake `sleep`), returns 404 (no retry), raises `httpx.ConnectError`, or sleeps longer than `timeout`. Files go into pytest's `tmp_path`. One test **cancels the whole `download_all` call** mid-way and checks that no `.part` file is left anywhere. Build it step by step: one URL, then many, then the limit, then retries, then timeouts, then cancellation, running the tests after each step.

## 19. Common traps

**Threads and processes**

1. **`target=f()` instead of `target=f`.** The function runs immediately in the main thread.
2. **Calling `run()` instead of `start()`.** No new thread; everything runs serially.
3. **Start-join-start-join.** Start all, then join all, or nothing overlaps.
4. **Exceptions in threads disappear.** Catch inside the thread, or use futures and call `result()`.
5. **"The GIL makes it safe."** It protects the interpreter, not your data. Lock every shared read-modify-write and check-then-act.
6. **Locking only the writes.** Readers must use the same lock, or they can see half-updated state.
7. **Slow work inside a lock.** Everyone else waits. Lock only the update of shared data.
8. **Nested locks in different orders.** Deadlock. Use one global lock order, or do not nest.
9. **A method holding a `Lock` calls another method that takes it.** Self-deadlock. Use `RLock` or an unlocked helper.
10. **One sentinel for several workers.** The other workers wait forever.
11. **Forgetting `task_done()` on error.** `queue.join()` hangs. Put it in `finally`.
12. **Daemon threads doing important work.** They are killed at exit without clean-up.
13. **`time.sleep(interval)` in a stoppable loop.** Use `stop_event.wait(interval)`.
14. **Threads for CPU-bound Python.** No speed-up on a normal build. Use processes.
15. **No `if __name__ == "__main__":` guard, lambdas or nested functions sent to a process pool.** Crash on spawn/forkserver.
16. **Sending big data to processes.** Copying costs more than the work. Send names, return small results.
17. **Expecting `future.cancel()` to stop a running job.** It only stops queued ones.

**asyncio**

18. **Forgetting `await`.** The coroutine never runs; watch for "was never awaited".
19. **Awaiting one by one when you meant concurrency.** Use `gather` or a `TaskGroup`.
20. **Blocking calls in `async def`** (`time.sleep`, `requests`, sync DB, heavy CPU). The whole loop freezes. Use async libraries, `to_thread` or a process executor.
21. **Fire-and-forget tasks without a reference.** They can vanish. Keep them in a set, or use a `TaskGroup`.
22. **Assuming `gather` cancels the others on failure.** It does not; `TaskGroup` does.
23. **`except ValueError` around a `TaskGroup`.** It raises an `ExceptionGroup`; use `except*`.
24. **Swallowing `CancelledError`.** Breaks timeouts, task groups and shutdown. Clean up in `finally`, re-raise.
25. **Cancelling without awaiting.** Clean-up has not run yet. Cancel, then `await` (with `return_exceptions=True`).
26. **An `await` inside a check-then-act.** A race even on one thread. Use `asyncio.Lock`.
27. **`threading.Lock` in async code.** Blocks the loop. Use `asyncio.Lock`.
28. **Unbounded `gather` over thousands of requests.** Use a semaphore or a worker pool.
29. **A new `httpx.AsyncClient` per request.** Slow; reuse one client.
30. **Trusting per-phase HTTP timeouts as a deadline.** Use `asyncio.timeout` for a total limit.
31. **Retrying 4xx errors, or retrying without backoff.** Retry only transport errors and 5xx, with growing delays.
32. **Tests that depend on exact timing.** Count (peak in flight, call counts, event order) instead, and use generous ratios when you must time.

## 20. Summary

- **I/O-bound** work waits; **CPU-bound** work computes. Measure first. Concurrency overlaps waits; parallelism runs computations on several cores at once.
- **Threads** share memory and are cheap. In normal CPython the **GIL** lets only one run Python code at a time, but blocking I/O releases it, so threads are great for waiting. Free-threaded builds (3.13t/3.14t) remove the GIL; locks are still needed.
- **Races** come from shared data plus multi-step updates (read-modify-write, check-then-act). Fix with a **`Lock`** around the whole critical section, kept inside the object that owns the data. **`RLock`** allows re-entry by the same thread.
- **Deadlocks** come from circles of waiting. Take locks in one global order, avoid nesting, use timeouts in tests, and `faulthandler` to see where threads are stuck.
- **`Event`** signals (and makes stoppable loops), **`Semaphore`** limits, **`Condition`** waits for a state, **`Barrier`** lines threads up, and **`queue.Queue`** passes work safely: sentinels, `task_done`/`join`, `maxsize` for backpressure.
- **Processes** give real parallelism but copy data by pickling: guard with `if __name__ == "__main__":`, keep worker functions top-level, share little (`Value`, `Array`, `Manager` when you must).
- **`concurrent.futures`**: one interface for thread and process pools. `submit` returns a future; `result()` re-raises errors; `map` keeps input order; `as_completed` gives completion order; `cancel` only stops queued work; `shutdown(cancel_futures=True)` drops the queue.
- **asyncio**: one thread, many tasks, switching only at `await`. Coroutines do nothing until awaited; `asyncio.run` starts the loop; `gather` and **`TaskGroup`** run tasks concurrently (TaskGroup cancels siblings on failure and raises an `ExceptionGroup`, caught with `except*`).
- **Timeouts** (`asyncio.timeout`) and **cancellation** work by raising `CancelledError` at an `await`. Clean up in `finally` and never swallow it. Cancel *and* await leftover tasks.
- **Bound** concurrency with `asyncio.Semaphore` or a worker pool on `asyncio.Queue`; keep the loop free of blocking calls with `to_thread` and `run_in_executor`; debug mode finds the offenders.
- **Async iterators, generators and context managers** (`async for`, `async def` + `yield`, `async with`, `aclose`, `@asynccontextmanager`) let waiting happen inside loops and set-up/clean-up.
- **httpx**: reuse one `AsyncClient`, `raise_for_status()`, retry only transport errors and 5xx with exponential backoff, use `asyncio.timeout` for real deadlines, pass the client in as a parameter, and test with `MockTransport`.
- The **project** combines all of it: limit, retry, timeout, `.part` files renamed on success, and clean cancellation.

Next, the problems. Start with the drills in each part (threads, then futures and asyncio, then httpx), and run every test file several times: a concurrency test that passes only sometimes is telling you about a race.
