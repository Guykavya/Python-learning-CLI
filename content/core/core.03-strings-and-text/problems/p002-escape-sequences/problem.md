# Print with escape sequences

Write a program that takes **no input** and prints exactly these five lines:

```
She said "It's fine"
C:\new\table
Name:	Asha
Price: ₹500
Tab→	←Tab
```

Details that matter:

- Line 1 contains both a double quote and a single quote.
- Line 2 contains real backslashes. It must not turn into a newline or a tab.
- Line 3 has a **tab character** between `Name:` and `Asha`, not spaces.
- Line 4 contains the rupee sign. Write it with the escape `\u20b9` (or `\N{INDIAN RUPEE SIGN}`) so your file works even on a keyboard without the symbol.
- Line 5 has a tab between the two arrows `→` (U+2192) and `←` (U+2190). Write the arrows any way you like.

You may use one `print()` per line, or fewer.
