## Hint 1

Write the Series as a two-row table: labels `2, 0, 1` on the left, values `10, 20, 30` on the right. Then, for each line, ask: does it say *label* (`s[0]`, `.loc`) or *position* (`.iloc`)?

## Hint 2

```text
label  value        s[0]       -> row labelled 0       -> 20
2      10           s.iloc[0]  -> first row            -> 10
0      20           s.loc[1]   -> row labelled 1       -> 30
1      30           s.iloc[-1] -> last row             -> 30
                    s.loc[[0, 1]] -> labels 0 then 1   -> [20, 30]
                    s.loc[5]   -> no such label        -> KeyError (print its class name)
```
