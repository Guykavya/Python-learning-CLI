## Hint 1

In one traceback the frames go from the outside in, so the innermost frame is the last frame
line. In a chain, the last traceback is printed last. So what is "the innermost frame of the
last traceback" in terms of the whole text? Do you need to split the text into blocks at all?

## Hint 2

How do you tell a frame line from a source line that happens to contain `File "`? Look at the
indentation. A regex with `re.MULTILINE` lets `^` mean "start of a line":
`^  File "(.+?)", line (\d+)`. The `, in <name>` part is optional, so put it in an optional
group `(?:, in (.+))?`.

## Hint 3

```
pattern = ^  File "(file)", line (digits)(?:, in (name))?$   with MULTILINE
matches = all matches in tb_text
if none: raise ValueError
last = matches[-1]
return (file, int(line), name or "")
```
