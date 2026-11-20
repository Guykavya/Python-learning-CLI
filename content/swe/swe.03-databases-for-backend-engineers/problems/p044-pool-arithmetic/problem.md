# Pool arithmetic

Chapter section 12.2. `QueuePool(pool_size=3, max_overflow=2, timeout=0.2)` keeps up to **3** connections ready in its queue and may open up to **2 extra** ("overflow") ones when all are in use: at most **5** at the same time. A sixth request **waits** for a connection to be returned and fails with a timeout after `timeout` seconds. Connections returned while the queue has room (fewer than 3 idle ones) go back to the queue; beyond that they are closed.

```python
from sqlalchemy.exc import TimeoutError as PoolTimeout
from sqlalchemy.pool import QueuePool


class Conn:
    def close(self):
        pass

    def rollback(self):
        pass

    def commit(self):
        pass


pool = QueuePool(Conn, pool_size=3, max_overflow=2, timeout=0.2)
held = {}


def show(label):
    print(f"{label}: checked_out={pool.checkedout()} checked_in={pool.checkedin()}")


for name in ["A", "B", "C", "D", "E"]:
    held[name] = pool.connect()
    show(f"checkout {name}")
try:
    held["F"] = pool.connect()
    show("checkout F")
except PoolTimeout:
    print("checkout F: timeout")
held["A"].close()
show("return A")
held["G"] = pool.connect()
show("checkout G")
held["B"].close()
held["C"].close()
show("return B and C")
held["D"].close()
show("return D")
```

Predict **exactly** the ten lines that are printed. `pool.checkedout()` is the number of connections in use right now; `pool.checkedin()` is the number of idle connections waiting in the queue. Do not run it.

Write your answer in `answer.txt`, one printed line per line.

## How to work

1. At the start the queue is empty: the pool creates connections **on demand**.
2. Keep two numbers while you walk through the events: `checked_out` and `checked_in`.
3. A checkout takes an idle connection if there is one; otherwise it creates a new one, up to `pool_size + max_overflow`.
4. A return puts the connection into the queue when the queue has fewer than `pool_size` idle connections.

## After you answer

1. Why does `checkout F` time out, and after how long?
2. After `return A` and `checkout G`, why is `checked_in` 0 again?
3. What would change if `max_overflow` were 0?
