# Decode bytes from hex

A network tool shows data as hex bytes. Read one line of hex digits (pairs may be separated by spaces) that hold UTF-8 text. Print:

```
Text: <the decoded text>
Bytes: <number of bytes>
Characters: <number of characters in the text>
```

**Example**

Input:
```
63 61 66 c3 a9
```
Output:
```
Text: café
Bytes: 5
Characters: 4
```
