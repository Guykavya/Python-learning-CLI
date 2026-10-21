1. **`"ERROR" in line`.** I only need yes or no. `in` gives a bool directly. `line.find("ERROR")` works too, but then I must remember that "not found" is -1, and a check like `> 0` would wrongly miss a match at position 0.

2. **`key, sep, value = line.partition("=")`.** It cuts once, at the first `=`, so a value like `a=b` stays whole. `line.split("=")` cuts at every `=`, so `token=abc=` would lose part of the value. `partition` also never fails: with no `=`, `sep` is empty, which I can check.

3. **`line.index("###")`.** It returns the position, and when the marker is missing it raises `ValueError`, so the bad file stops the program with a clear message. `find` would return -1, and using -1 as a position quietly points at the last character, giving wrong results with no error.

4. **`name.removesuffix(".csv")`.** It removes that exact ending once, only if it is there. `rstrip(".csv")` treats its argument as a set of characters `.`, `c`, `s`, `v` and keeps removing them, so `docs.csv` becomes `do`.

5. **`typed.casefold() == stored.casefold()`.** `casefold` is designed for caseless comparison across languages. `lower()` leaves `ß` alone, so `Straße` and `STRASSE` would not match. For full safety I would also normalise both with `unicodedata.normalize("NFC", ...)` first.

Key ideas to check: `in` for yes/no; `partition` cuts once and never fails; `index` fails loudly while `find`'s -1 is a valid index; `strip` family takes a set of characters; `casefold` for caseless comparison.
