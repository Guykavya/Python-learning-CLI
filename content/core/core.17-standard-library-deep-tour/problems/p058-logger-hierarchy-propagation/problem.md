# Trace: logger hierarchy, levels and propagation

Logger names with dots form a tree: `shop.db.pool` is a child of `shop.db`, which is a child of
`shop`, which is a child of the root logger. The rules for one call such as `pool.warning("p2")`:

1. **Is the level enabled?** Only the level of the logger you call is checked. If that logger has no
   level of its own (`NOTSET`), its **effective level** is the first level set on the way up to the
   root (the root's default is `WARNING`).
2. If yes, a record is created and given to the handlers of **this** logger, then of its parent, its
   grandparent, ... Each **handler** checks its own level. The parent **loggers'** levels are *not*
   checked again on the way up.
3. The climb stops after a logger whose `propagate` is `False`.
4. If the climb found **no handler at all**, Python uses `logging.lastResort`: it prints just the
   message to **stderr**, for `WARNING` and above.

What does this program print? `print` lines and log lines both go to the screen.

```python
import logging
import sys


def handler(tag, level=logging.NOTSET):
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    h.setFormatter(logging.Formatter(tag + " %(name)s %(levelname)s %(message)s"))
    return h


shop = logging.getLogger("shop")
shop.setLevel(logging.INFO)
shop.addHandler(handler("[shop]"))

db = logging.getLogger("shop.db")
db.addHandler(handler("[db]", logging.WARNING))

pool = logging.getLogger("shop.db.pool")
pool.setLevel(logging.DEBUG)

web = logging.getLogger("shop.web")
web.propagate = False
web.addHandler(handler("[web]"))

print(logging.getLevelName(db.getEffectiveLevel()), logging.getLevelName(pool.getEffectiveLevel()))
pool.debug("p1")
db.debug("d1")
db.info("d2")
db.error("d3")
web.info("w1")
web.debug("w2")
logging.getLogger("shop.web.api").warning("a1")
print(logging.getLogger("shop.web.api").parent.name, logging.getLogger("shop.db") is db)
shop.warning("s1")
db.setLevel(logging.ERROR)
pool.warning("p2")
db.warning("d4")
pool.propagate = False
pool.critical("p3")
print("end")
```

Notes:

- The root logger has no handlers in this program (nobody called `basicConfig`).
- A handler made with `level=logging.NOTSET` lets every record through.
- Each handler writes and flushes immediately, so lines appear in the order the calls happen.

Write the exact output, one line per printed line, in `answer.txt`.
