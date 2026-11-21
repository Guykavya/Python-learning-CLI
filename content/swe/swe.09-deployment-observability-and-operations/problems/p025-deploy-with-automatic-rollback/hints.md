## Hint 1

Which operations must never be seen half-done? List them (a release folder, the pointer) and ask, for each, which single operation makes it appear all at once. Then list the states after a failed health check and ask what must be true: which version is live, what happens to the new folder, what if there was no old version?

## Hint 2

```text
validate version and every file path (before writing)
tmp = releases/.<version>.tmp  -> write all files -> os.replace(tmp, releases/<version>)     (on error: remove tmp, re-raise)
previous = current_version(root)
write the pointer: current.tmp -> os.replace -> current ;  append the version to history.txt
healthy = bool(health_check(release_dir))   (an exception means failure; keep "ExceptionName: message")
healthy -> live | failed with previous -> write pointer back | failed without previous -> delete current
prune: existing = history order filtered by existing folders; delete the oldest non-live ones until len == keep
```
