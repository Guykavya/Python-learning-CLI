## Hint 1

`shlex.split` has a `comments` parameter. What is its default? What does `shlex.join` do that
`" ".join` does not? Try `" ".join(["rm", "x; rm -rf ~"])` and think about what a shell would run.

## Hint 2

For `parse_settings`, reuse the shell-style split. Then for each token, `token.partition("=")`
returns `(key, "=", value)`, split at the first `=` only; the middle part is `""` when there is no
`=` at all. Which two cases are errors?

## Hint 3

```
split_command:  return shlex.split(line, comments=True)
join_command:   return shlex.join(args)
parse_settings: result = {}
                for token in split_command(line):
                    key, sep, value = token.partition("=")
                    if not sep or not key: raise ValueError
                    result[key] = value
                return result
```
