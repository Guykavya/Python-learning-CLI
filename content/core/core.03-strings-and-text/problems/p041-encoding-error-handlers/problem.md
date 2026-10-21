# Compare the error handlers

Some old systems accept only ASCII. Read a line of text and encode it to ASCII with four different error handlers. Decode each result back with ASCII so you print text, not `b'...'`:

```
ignore: <text encoded with errors="ignore">
replace: <errors="replace">
xml: <errors="xmlcharrefreplace">
backslash: <errors="backslashreplace">
Lost: <how many characters "ignore" dropped>
```

**Example**

Input:
```
café 🙂
```
Output:
```
ignore: caf 
replace: caf? ?
xml: caf&#233; &#128578;
backslash: caf\xe9 \U0001f642
Lost: 2
```

(The `ignore` line ends with a space; the checker ignores spaces at the end of a line.)
