## Approach

The key idea is one sentence: **unpickling is running code that the file's author chose**. Everything else
follows: you cannot inspect the file safely, so you must not load files you do not trust, and for outside data
you pick a format that cannot contain instructions.

## Model answer

See `answer.md` for the model answer.

## Complexity

Not applicable: this is a written answer.

## Another way

Try the harmless version yourself in the shell: build a small class whose `__reduce__` method returns
`(print, ("loaded!",))`, pickle it, and unpickle it. You will see `loaded!` printed by `pickle.loads` itself. Then
think how bad it would be if `print` were another function.
