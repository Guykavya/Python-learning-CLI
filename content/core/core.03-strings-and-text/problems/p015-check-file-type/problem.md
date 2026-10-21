# What kind of file?

Read a file name. Print three lines:

```
Image: <True if it ends with .png, .jpg, .jpeg or .gif, in any case>
Hidden: <True if it starts with a dot>
Backup: <True if it ends with ~ or .bak>
```

**Example**

Input:
```
Holiday.JPG
```
Output:
```
Image: True
Hidden: False
Backup: False
```

You do not need `if`: these methods already return `True` or `False`.
