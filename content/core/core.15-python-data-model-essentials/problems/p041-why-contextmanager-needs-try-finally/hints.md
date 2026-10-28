## Hint 1

Where is the generator paused while the `with` block runs? What does `@contextmanager` do to the generator when the block raises: does it just stop calling it, or does it do something at the `yield` line?

## Hint 2

Think of what `yield` does when an exception is thrown in at that point: it raises the exception, exactly as if you had written `raise` there. Which Python statement guarantees code runs while an exception passes through a block?

## Hint 3

Plan of the answer:

```text
1. exception is raised AT the yield; code after yield is skipped when the yield raises; finally runs
2. __exit__ always runs; @contextmanager's __exit__ resumes the generator with throw(exc)
3. try: yield ... finally: clean-up
4. file/lock/socket/env var/cwd/transaction; say what breaks (leak, deadlock, wrong state)
```
