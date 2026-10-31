## Hint 1

One name is `[\w'-]+`. First names are one name, then optionally more ` name` pieces:
`[\w'-]+(?: [\w'-]+)*`. Put a group around the last name and one around the first names. In
the replacement, which order do the groups go in?

## Hint 2

`^` and `$` must mean the start and end of **each line**. Which flag does that? And why is
`\s*` after the comma dangerous here? (`\s` also matches `\n`: try `"Doe,\nJane"`.) Use
`[ \t]*` instead.

## Hint 3

```
pattern = ^([\w'-]+),[ \t]*([\w'-]+(?: [\w'-]+)*)[ \t]*$
return re.sub(pattern, r"\2 \1", text, flags=re.MULTILINE)
```
