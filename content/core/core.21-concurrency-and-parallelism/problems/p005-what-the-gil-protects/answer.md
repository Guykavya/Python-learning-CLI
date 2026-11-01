**1. What the GIL is.** The Global Interpreter Lock is one lock inside CPython. A thread must
hold it to run Python bytecode. It protects the **interpreter's own data** (reference counts,
object internals, the memory allocator), so CPython itself never crashes from two threads
touching the same object at the same moment. A thread gives it up in two ways: **voluntarily**
when it starts a blocking operation (reading a socket or file, `time.sleep`, waiting on a lock,
many C extensions such as hashing or NumPy maths), and **forcibly** when another thread is
waiting: about every 5 ms (`sys.getswitchinterval()`) the running thread is asked to drop it
between two bytecodes.

**2. Why `counter += 1` is a race.** It is four bytecodes: read, push 1, add, store. The forced
switch can happen between the read and the store. Thread A reads 10, is switched out; thread B
reads 10, stores 11; A wakes up and stores its own 11. One increment is lost. The GIL makes each
single bytecode safe, not your **sequence** of them. Protecting a read-modify-write needs your
own `threading.Lock` around all of it.

**3. Speed.** CPU-bound threads all need the GIL to run bytecode, so only one of them makes
progress at any moment; four threads on four cores still run about as fast as one (often a bit
slower, because of switching). For CPU work use processes. I/O-bound threads spend most of their
time **waiting with the GIL released**, so their waits overlap: 20 downloads of 1 s each take
about 1 s in 20 threads. So threads are very useful in Python, just for waiting, not computing.

**4. Free-threaded Python.** Since 3.13 there is a separate build (`python3.13t`, `python3.14t`;
officially supported in 3.14) with no GIL. Threads then run Python code truly in parallel on
several cores, so CPU-bound threads can speed up. The interpreter protects its own objects with
finer, per-object locks instead. A program can check with `sys._is_gil_enabled()` (`False` when
running without the GIL) and `sysconfig.get_config_var("Py_GIL_DISABLED")` (whether the build
supports it). For `counter += 1` nothing gets better: the race is **more** likely, because
threads really do run at the same time.

**5. Advice.** Never rely on the GIL for correctness: protect every shared read-modify-write
with a lock (or avoid sharing, and pass data through a `queue.Queue`), and choose threads for
waiting and processes (or the free-threaded build) for computing.
