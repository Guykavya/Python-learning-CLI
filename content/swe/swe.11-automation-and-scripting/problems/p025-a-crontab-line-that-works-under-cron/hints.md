## Hint 1

Validate first, build second. Which three facts about the schedule tell you it is well formed (how many words, and what the single-word form starts with)? Which method of `PurePosixPath` tells you a path is absolute? Build the command part as one string, escape `%` in it, and only then put the schedule in front.

## Hint 2

```text
fields = schedule.split()
if not (len(fields) == 5 or (len(fields) == 1 and fields[0].startswith("@"))): raise ValueError
for name, p in (("python", python), ("script", script), ("log", log)):
    if not PurePosixPath(p).is_absolute(): raise ValueError(f"{name} must be an absolute path: {p}")
for word in [python, script, log, *args]: if " " in str(word): raise ValueError
command = f"cd {PurePosixPath(script).parent} && " + " ".join([python, script, *args]) + f" >> {log} 2>&1"
return " ".join(fields) + " " + command.replace("%", "\\%")
```
