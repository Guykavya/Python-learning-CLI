# First word and the rest

Read a line such as a command typed into a chat bot. Remove spaces at both ends, then split it at the **first** space into the command and the rest. Print:

```
Command: <first word>
Rest: <everything after the first space>
```

**Example**

Input:
```
  say hello to   everyone
```
Output:
```
Command: say
Rest: hello to   everyone
```

The rest keeps its inner spaces exactly. If there is no space, the rest is empty, so the second line is just `Rest:` (a trailing space after the colon does not matter).
