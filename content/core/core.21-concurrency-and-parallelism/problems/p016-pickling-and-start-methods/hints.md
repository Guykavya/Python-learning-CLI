## Hint 1

Try it yourself: `pickle.dumps(len)` works, `pickle.dumps(lambda x: x)` fails. Look at
`pickle.dumps(some_top_level_function)` with `pickletools.dis(...)`: what is actually stored,
the code or a name? How would the worker turn that back into a function?

## Hint 2

Draw the life of one task under spawn:

```
parent: pickle (module name, function name, args)  -> bytes over a pipe
child:  start Python -> import your script as __mp_main__ (runs its top level!)
        -> look up the function by name -> call it -> pickle the result (or exception)
parent: unpickle the result
```

Each arrow is a place where something must be picklable or importable, and each step is a
cost that threads do not pay.
