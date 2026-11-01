- Using threads for CPU-heavy Python code and expecting a speed-up. With the GIL only one
  thread runs Python bytecode at a time; the threaded version is often slightly *slower*.
- Using processes for downloads. It works, but each process costs memory and start-up time,
  and the CPU was idle anyway.
- Calling a blocking library (`requests.get`, `time.sleep`) inside `async def`. The whole event
  loop stops until it returns. Use threads, `asyncio.to_thread`, or an async library.
- One thread per connection for thousands of connections. Each thread has its own stack and the
  OS has to switch between them; asyncio tasks are much lighter.
- Adding concurrency to a job that takes milliseconds. More code, more bugs, no gain.
- Treating a two-stage job as one kind. "Download then process" needs a different tool for
  each stage.
