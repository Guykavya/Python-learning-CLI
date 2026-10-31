## Hint 1

For `<.*>`: the `.*` first runs to the end of the string, then gives back one character at a time until a `>` can match. Which `>` is the first one it reaches going **backwards**? For `<.*?>`: the `.*?` starts empty and grows one character at a time until a `>` fits. Which `>` is the first one going **forwards**?

## Hint 2

`\d{2,4}` takes 4 if it can; `\d{2,4}?` takes 2 if it can. With `findall`, each next search starts where the last match ended, so count what is left over at the end of `"1234567"`. For `x.*?$`, the lazy part must keep growing until `$` can match: where is that?

## Hint 3

```
<.*>     -> one match, from the first < to the LAST >
<.*?>    -> each tag; <[^>]*> -> same tags, without any backtracking
\d{2,4}  -> 1234 ; lazy -> 12 ; findall greedy: 1234, 567 ; lazy: 12 34 56 (7 is alone)
a.*b -> up to the last b ; a.*?b -> up to the first b
\w+? findall -> one char each ; \s+? sub -> each space replaced separately
<(.+?)> on "<<a>>": starts at 0, group must reach the first > it can
colou??r: lazy u is skipped first, then taken because 'r' fails
\d+?\d -> two digits ; \d+?$ -> must reach the end
```
