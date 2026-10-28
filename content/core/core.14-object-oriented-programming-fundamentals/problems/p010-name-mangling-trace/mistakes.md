- Thinking `__pin` is truly private and `v._Vault__pin` fails. Mangling only renames; it does not hide.
- Mangling the bottom lines too. Code outside a class is not rewritten, so `v.__pin` looks for `__pin`.
- Expecting `s.reveal()` to give `silver / 9999`. `reveal` was written in `Vault`, so it uses the
  `_Vault__` names; the subclass's names are separate.
- Thinking `self.__pin = 9999` in `SubVault` overwrites the parent's pin. It creates `_SubVault__pin`.
- Thinking `v.__pin = 0` changes the pin used by `reveal`. It adds a new, unrelated attribute.
- Sorting `owner` before the underscore names. In ASCII, `_` (95) comes before `o` (111).
