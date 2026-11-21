## Hint 1

Read the script as a timeline and ask at each line: "if the process stops here, or the check fails, what do users get?" The first line already changes what users get, before there is anything to serve. The last lines remove the one thing a rollback needs.

## Hint 2

The three bugs: (1) the pointer is switched **before** the release exists, and the release is written in place, so a write error leaves the pointer naming a half-written folder; (2) the previous release is deleted before anyone knows the new one works; (3) nothing restores the pointer when the health check fails (or raises).

```text
write all files into releases/.<version>.tmp ; os.replace(tmp, releases/<version>)   (clean up tmp on error)
switch the pointer (current.tmp -> os.replace)
healthy = check(target)   (an exception counts as False)
if not healthy: pointer back to previous, or removed when there was none
never rmtree the previous release
```
