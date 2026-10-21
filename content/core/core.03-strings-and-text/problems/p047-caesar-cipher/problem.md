# Caesar cipher

A Caesar cipher replaces every letter with the letter a fixed number of places further along the alphabet, wrapping from `z` back to `a`. With a shift of 3, `a` becomes `d`, `x` becomes `a`, and `Hello` becomes `Khoor`.

Read a shift (a whole number, possibly negative or larger than 26) and then a line of text. Print the text with every **English** letter shifted. Keep the case of each letter. Everything else (spaces, digits, punctuation, accented letters, emoji) stays unchanged.

**Example**

Input:
```
3
Hello, World!
```
Output:
```
Khoor, Zruog!
```

A shift of 29 is the same as 3, and a shift of -3 undoes a shift of 3.

You cannot use loops. Build a translation table with `str.maketrans` and slicing.
