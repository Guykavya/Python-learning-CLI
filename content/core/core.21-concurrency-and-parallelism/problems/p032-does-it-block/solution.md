## Approach

The model answer is in `answer.md`. The idea behind it: every line inside `async def` falls
into one of four groups.

| Group | Snippets | Blocks? | Fix |
|---|---|---|---|
| `await` on async I/O or `asyncio.sleep` | 3, 6 | no | none |
| sync waiting (sleep, network, database) | 1, 2, 8 | yes, as long as the wait | `asyncio.to_thread(...)` or an async library |
| long CPU work | 4, 7 | yes, seconds | `run_in_executor` with a `ProcessPoolExecutor` |
| tiny work | 5 | microseconds | leave it |

## Check your answer

- Did you say that writing `async def` does **not** make the lines inside it non-blocking?
- Did you separate **waiting** (a thread is enough, because blocking I/O releases the GIL)
  from **computing** (needs a process, because of the GIL)?
- Did you accept the small file read instead of "fixing" it? Judgement about duration is part
  of the skill.
- Did you write `to_thread(func, arg)` and not `to_thread(func(arg))`?
- Did you name a real async replacement for `requests` (`httpx.AsyncClient`, `aiohttp`)?

## Complexity

Not relevant for an explain problem.

## Another way

You can let Python find blocking code for you: run with `PYTHONASYNCIODEBUG=1` (or
`asyncio.run(main(), debug=True)`). In debug mode the loop logs a warning like
`Executing <Task ...> took 2.003 seconds` for every step that holds the loop longer than
`loop.slow_callback_duration` (0.1 s by default).
