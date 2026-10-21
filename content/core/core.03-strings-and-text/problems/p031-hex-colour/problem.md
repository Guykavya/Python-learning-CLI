# Hex colour codes

Web colours are written as six hex digits, like `#1E90ff`: two digits each for red, green and blue. Read a colour code (the `#` may or may not be there, and the letters may be any case). Print:

```
rgb(<red>, <green>, <blue>)
<the code normalised to lowercase with a #>
```

**Example**

Input:
```
1E90ff
```
Output:
```
rgb(30, 144, 255)
#1e90ff
```

`int("ff", 16)` turns hex text into a number. The format type `x` turns a number back into hex.
