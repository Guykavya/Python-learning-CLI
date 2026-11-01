- Writing `f1 exception: 10` or leaving the line out. `exception()` of a successful future is
  `None`, and `print` shows `None`.
- Writing `f2 exception: bad 3`. The program prints `repr(...)`, which includes the class
  name and quotes: `ValueError('bad 3')`.
- Thinking `f2.done()` is `False` because the job failed. "Done" means "finished for any
  reason": value, exception or cancelled.
- Expecting `cancel b: True`. A running job cannot be cancelled; `cancel()` returns `False`
  and the job keeps running.
- Expecting `q.result()` to return `None` after cancel. It raises `CancelledError`.
- Expecting `ex.map(...)` itself to raise, so `map returned an iterator` is missing. `map`
  only submits; the error comes out when the loop reaches item 3.
- Adding `got 40`. Once the iterator raises, the loop is over; item 4's result is thrown away.
