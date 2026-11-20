## Approach

Separate **waiting** from **working**. Most of a web request's time is waiting (for the network, a database, another API). WSGI holds a thread for the whole wait; ASGI lets one thread switch to other work at each `await`. And because `receive` and `send` can be called many times, ASGI can model a connection that lives for a long time.

See `answer.md` for a model answer and a checklist. The key sentence: **WSGI is one call, one response, one blocked thread; ASGI is one call per connection, with many awaitable messages, sharing one event loop.**

Example: with one worker, WSGI serves the 5 ms request after about 2 s; an async app with an `await`ed API call serves it after about 5 ms.

## Complexity

Not applicable.

## Another way

Explain it with a restaurant: a WSGI waiter takes one order and stands at the kitchen door until the food is ready; an ASGI waiter takes an order, gives it to the kitchen, and serves other tables until the kitchen rings the bell. A WebSocket is a table that keeps ordering all evening. A waiter who cooks the meal himself (CPU work) helps nobody else in the meantime.
