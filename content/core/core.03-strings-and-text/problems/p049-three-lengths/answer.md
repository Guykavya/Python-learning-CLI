**1. Three lengths.**
- *Code points*: the units a Python `str` is made of. `len()` counts these.
- *Bytes*: how much space the text takes after encoding, for example in UTF-8. `len(s.encode("utf-8"))`.
- *Grapheme clusters*: what a human sees as one character. Python's standard library has no simple function for this; the third-party `regex` module (`\X`) or the `grapheme` package can count them.

**2. The three strings.**
- `🇮🇳` is two code points, REGIONAL INDICATOR I and REGIONAL INDICATOR N. Phones draw the pair as a flag. Each is above U+FFFF, so 4 bytes each: `len` 2, bytes 8.
- `👨‍👩‍👧` is man, ZERO WIDTH JOINER, woman, ZWJ, girl: 5 code points. The three people take 4 bytes each, and each ZWJ (U+200D) takes 3: 12 + 6 = 18 bytes.
- `"café"` is c, a, f, e, COMBINING ACUTE ACCENT: 5 code points. The accent (U+0301) takes 2 bytes, the rest 1 each: 6 bytes.

**3. When each matters.**
- *Bytes*: a database column declared as 255 bytes, a network message size, a file size.
- *Grapheme clusters*: a "maximum 280 characters" limit shown to users, cursor movement in a text box, or counting letters for a word game.
- *Code points*: Python indexing and slicing, and many APIs that say "characters" but mean code points.

**4. Cutting.** `s[:10]` cuts after 10 code points. It can leave an `e` without its accent, or cut a family after the man and a joiner, showing a broken emoji. Cutting the UTF-8 bytes at a fixed position is worse: it can split one code point in the middle, so decoding gives `UnicodeDecodeError` or a `�` replacement character. Safer: cut on code points at word boundaries (`textwrap.shorten`), or use a grapheme-aware library.

**5. Normalisation.** NFC combines `e` + U+0301 into the single code point `é` (U+00E9), so the word becomes 4 code points and 5 bytes, matching what a user sees. A flag or a family has no single precomposed code point, so normalisation leaves them as they are. They remain several code points that display as one picture.

Key ideas to check: code points versus bytes versus graphemes; `len` counts code points; regional indicators and ZWJ sequences; combining marks; byte limits versus user-visible limits; slicing can break graphemes and byte cuts can break code points; NFC only fixes composable characters.
