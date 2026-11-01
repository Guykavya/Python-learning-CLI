## Hint 1

Go block by block. For each `print`, ask: which thread runs this line, and what has
**definitely** happened before it? `a.join()` means "A's greet has finished". `started.wait()`
means "C has printed its first line". Which thread name does `greet` see when you call
`b.run()` instead of `b.start()`?

## Hint 2

Write a timeline with two columns:

```
main thread                          worker
created, alive: False
a.start() -> a.join() waits          A runs in worker-A
A joined, alive: ...
b.run(): greet runs HERE, in main
c.start(); started.wait() waits      C: started; started.set(); go.wait() waits
main: C alive? ...                   (still waiting)
main: keeps going ...
go.set(); c.join() waits             C: finished
...
```

Is a thread that is blocked in `go.wait()` alive? Was `b` ever started?
