## Hint 1

What does the word "w" do to a file that already has content? When exactly does it do that: at `open`, or at the
first `write`? Imagine the program dies after `open` but before `write` finishes.

## Hint 2

Answer in four short parts: (1) `"w"` truncates at once, so a crash leaves an empty or half file;
(2) write a temp file, then `os.replace`, so readers see old or new; (3) atomic = all or nothing, same disk so it is
only a rename; (4) `flush` + `fsync` before replace, and the pattern does not solve two writers at once.
