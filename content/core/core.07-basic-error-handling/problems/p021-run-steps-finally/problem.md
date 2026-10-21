# Steps with guaranteed clean-up

A small job runner runs named steps and writes a log. Write `run_steps(steps, log)` where `steps`
is a list of `(name, func)` pairs and `log` is a list to append messages to. For each step, in
order:

1. append `"start <name>"`;
2. call `func()`;
3. - if it succeeded: append `"done <name>"`;
   - if it raised `ValueError`: append `"failed <name>: <message>"` and carry on with the next step;
4. **always** append `"end <name>"` as the last message for that step, using `finally`.

Any other exception stops the whole run: it must propagate to the caller, but only **after**
`"end <name>"` has been logged for that step. Later steps do not run.

Return the number of steps that succeeded.

**Example**

```python
def ok(): pass
def bad(): raise ValueError("disk full")

log = []
run_steps([("backup", ok), ("upload", bad), ("report", ok)], log)   # 2
log
# ['start backup', 'done backup', 'end backup',
#  'start upload', 'failed upload: disk full', 'end upload',
#  'start report', 'done report', 'end report']
```
