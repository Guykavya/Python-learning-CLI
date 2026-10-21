See the model answer shown when you check. The ideas that must appear:

- Three lengths: code points (`len`), encoded bytes, grapheme clusters (what people see).
- The flag is 2 code points and 8 bytes; the family is 5 code points and 18 bytes; the word is 5 code points and 6 bytes.
- Bytes matter for storage limits and network sizes; graphemes matter for display and user-facing limits; code points are what Python indexes.
- Slicing can cut between a letter and its accent or inside an emoji sequence; cutting bytes can split a code point and make invalid UTF-8.
- NFC combines `e` + U+0301 into `é` (4 code points); flags and families have no single-code-point form.
