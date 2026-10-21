## Hint 1

Which one holds code points and which one holds numbers 0 to 255? Which one does a file or network really contain?

## Hint 2

In UTF-8, `é` is two bytes. In older encodings such as latin-1 or cp1252, `é` is the single byte `0xe9`. What does a UTF-8 decoder think `0xe9` means?

## Hint 3

Find out the real encoding (probably `cp1252` or `latin-1`) and decode with it. Compare what `ignore` and `replace` do to the name `José`.
