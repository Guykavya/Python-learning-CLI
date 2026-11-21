## Hint 1

Before checking any rule, turn the text into a list of *instructions*: join the lines that end with a backslash and remember the number of the first line. What would break if you checked line by line?

## Hint 2

```text
instructions = [(line_number, KEYWORD, rest), ...]        # comments and blank lines skipped
walk them once, remembering: stage names seen, the line of the first "pip install" RUN,
    the lines of "copy the whole context", and the last USER of the current stage (reset it at every FROM)
FROM:  image = first token without --flags; tagged? "latest"? digest? scratch? stage name? contains "$"?
CMD / ENTRYPOINT: rest does not start with "["  -> shell-cmd
COPY / ADD: any source (all tokens but the last, without --flags) in (".", "./")
ENV / ARG: shlex.split(rest) -> NAME=value pairs (or the old "ENV NAME value")
after the walk: copy-all lines before the install line; USER check (line 0)
```
