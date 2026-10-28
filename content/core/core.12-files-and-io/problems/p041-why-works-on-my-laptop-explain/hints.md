## Hint 1

Where does Python get the encoding from when you give none? Is that the same on Linux and Windows?
What is the first character you would see if the file starts with the three bytes `EF BB BF`?

## Hint 2

Four parts: (1) default = decided by the system, so it differs; (2) BOM = marker bytes at the start, shows as
`\ufeff` with `utf-8`, use `utf-8-sig`; (3) text mode translates `\r\n` to `\n` on read and `\n` to the system
ending on write, `newline=""` switches that off; (4) three rules: always `encoding=`, `newline=""` for csv, decide
`errors=`.
