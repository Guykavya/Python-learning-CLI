**1. Default encoding.** When you do not pass `encoding=`, Python asks the operating system for its preferred
encoding. On many Linux systems this is UTF-8. On Windows it can be a legacy code page like cp1252. The same
bytes then become different characters. `Zoë` saved as UTF-8 has two bytes for `ë`. A reader that uses cp1252 sees
two separate characters and prints `ZoÃ«`. Some bytes are not valid in the other encoding at all, and then you get a
`UnicodeDecodeError`.

**2. BOM.** A BOM (byte order mark) is a short marker, the bytes `EF BB BF`, that some programs such as Excel put at
the start of a UTF-8 file. With `encoding="utf-8"` it is read as a real character, `\ufeff`, which is invisible, so the
first header or name looks different and comparisons fail. `encoding="utf-8-sig"` removes it when reading (and
adds it when writing).

**3. Newline translation.** In text mode, when reading, `\r\n` and `\r` become `\n`. When writing, `\n` becomes the
system line ending, which is `\r\n` on Windows. So the bytes differ between systems. `newline=""` turns translation off
for reading (line endings are kept as they are) and for writing; `newline="\n"` on writing always gives `\n`. The
`csv` module needs `newline=""`.

**4. Rules.** Always write `encoding="utf-8"` (or `utf-8-sig` for Excel files). Always pass `newline=""` when using
`csv`, and say `newline="\n"` if exact bytes matter. Decide what to do with bad bytes: strict stops, `errors="replace"` goes on.
