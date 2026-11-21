## Hint 1

Who splits the command into words today? The **shell**, using its own rules for spaces, quotes, `;` and `$(...)`. If you hand `subprocess.run` a list, nobody splits anything: each list item reaches the child as exactly one entry of `sys.argv`. Which parameter then becomes unnecessary (and dangerous)?

## Hint 2

```text
result = subprocess.run([sys.executable, "-c", COUNT, str(filename)],
                        capture_output=True, text=True, check=True, timeout=10)
return int(result.stdout.strip())
```
