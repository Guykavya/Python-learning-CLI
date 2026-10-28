## Hint 1

Start with the first `print`: `db` has no level of its own. Which ancestor has one? `pool` has its own
level. Then, for each log call, first ask "does the logger I am calling let this level through?"
(only its effective level counts) and only then "which handlers does it reach?"

## Hint 2

Draw the tree with handlers: `shop` [shop handler, any level], `shop.db` [db handler, WARNING+],
`shop.db.pool` [none], `shop.web` [web handler, any level, propagate False], `shop.web.api` [none].
A record from `pool` visits pool, then db, then shop, then root. A record from `shop.web.api` visits
api, then web, and stops there.

## Hint 3

After `db.setLevel(logging.ERROR)`: `db.warning` is dropped at once, but `pool` has its own level
(DEBUG), so `pool.warning` passes and still reaches the handlers of `db` and `shop`. Finally `pool`
stops propagating and has no handler of its own: which last-resort rule applies to a CRITICAL record,
and what exactly does it print?
