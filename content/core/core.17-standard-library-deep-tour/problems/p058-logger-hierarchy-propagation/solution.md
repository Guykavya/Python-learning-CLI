## Walkthrough

| Call | Logger check | Handlers reached | Printed |
|---|---|---|---|
| first `print` | db: no level, parent `shop` is INFO; pool: own DEBUG | | `INFO DEBUG` |
| `pool.debug("p1")` | pool is DEBUG: passes | pool none; db handler needs WARNING: no; shop handler: yes | `[shop] shop.db.pool DEBUG p1` |
| `db.debug("d1")` | db's effective level INFO: dropped | | nothing |
| `db.info("d2")` | passes | db handler WARNING: no; shop: yes | `[shop] shop.db INFO d2` |
| `db.error("d3")` | passes | db handler: yes; shop: yes | two lines, `[db]` first |
| `web.info("w1")` | web's effective level INFO (from shop) | web handler; propagate False stops | `[web] shop.web INFO w1` |
| `web.debug("w2")` | dropped | | nothing |
| `api.warning("a1")` | api's effective level INFO | api none; web handler; stop | `[web] shop.web.api WARNING a1` |
| second `print` | parent of `shop.web.api` is `shop.web`; `getLogger` returns the same object | | `shop.web True` |
| `shop.warning("s1")` | passes | shop handler (root has none) | `[shop] shop WARNING s1` |
| `pool.warning("p2")` | pool's own DEBUG level, db's new ERROR level is **not** checked | db handler: yes; shop: yes | two lines |
| `db.warning("d4")` | db is now ERROR: dropped | | nothing |
| `pool.critical("p3")` | passes, but propagate False and pool has no handler | none found: `lastResort` | `p3` (on stderr, message only) |
| last `print` | | | `end` |

## The exact output

```text
INFO DEBUG
[shop] shop.db.pool DEBUG p1
[shop] shop.db INFO d2
[db] shop.db ERROR d3
[shop] shop.db ERROR d3
[web] shop.web INFO w1
[web] shop.web.api WARNING a1
shop.web True
[shop] shop WARNING s1
[db] shop.db.pool WARNING p2
[shop] shop.db.pool WARNING p2
p3
end
```

The two lessons: a logger's level is a gate only for calls made **on that logger** (or on children
without their own level), and handler levels filter what each destination shows.
