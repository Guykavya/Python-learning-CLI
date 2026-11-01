## Approach

The model answer is in `answer.md`. Everything follows from one fact: **processes do not share
memory, so everything travels as pickled bytes, and functions travel by name.**

| Question | Short answer |
|---|---|
| Why lambdas fail | pickle stores `module.name`; `<lambda>` cannot be looked up |
| What must pickle | function, arguments, return values, exceptions, initializer args, queue items |
| Why the guard | spawn/forkserver children import your script; top-level pool code would run again |
| spawn | fresh interpreter + import; default on Windows, macOS |
| fork | copy of the parent; fast, unsafe with threads; Linux/macOS only |
| forkserver | fork from a clean helper process; Linux default since 3.14 |
| Cost | interpreter start-up and memory, plus pickling and copying data both ways |

## Check your answer

- Did you say that pickle sends the function's **name**, not its code?
- Did you include return values and exceptions in the list of things that must be picklable?
- Did you explain that the child **imports** the script, so top-level code runs again?
- Did you give the 3.14 Linux default correctly (`forkserver`), and Windows/macOS (`spawn`)?
- Did you name the threads-plus-fork danger (copied locks that are never released)?
- Did you end with a top-level `def` **and** the guard?

## Another way

`concurrent.futures.ProcessPoolExecutor` has the same rules (it uses `multiprocessing`
inside). Libraries such as `cloudpickle` can pickle lambdas by sending their code, which is why
some frameworks accept them; the standard library does not. If you only need to fix arguments
of a top-level function, `functools.partial(top_level_fn, extra=1)` **is** picklable.
