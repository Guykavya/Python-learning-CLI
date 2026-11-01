## Hint 1

For each `is`, first ask: is the value an int between -5 and 256? If yes, every way of making it
returns the one cached object. If no, did the program make one object and reuse it, or make two
separate objects? What does `sys.intern` return for the second of two equal strings?

## Hint 2

```
int in -5..256 made at run time      -> cached object, so `is` is True
int outside, made twice              -> two objects, `is` is False (== still True)
float / joined str made twice        -> two objects
sys.intern(s1), sys.intern(s2)        -> the same stored object for equal text
[obj] * 3                            -> the SAME object three times (one id)
```
