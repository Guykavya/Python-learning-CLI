## Hint 1

First rewrite the program by hand: inside `Vault`, replace every `__secret` with `_Vault__secret`
and every `__pin` with `_Vault__pin`. Inside `SubVault`, use `_SubVault__...`. Leave the bottom part
(outside the classes) exactly as it is. Now the program has no magic left; which attributes exist?

## Hint 2

After rewriting:

```
Vault:    _Vault__secret = "gold";  __init__ sets owner, _Vault__pin = 1234
          reveal() reads self._Vault__secret and self._Vault__pin
SubVault: _SubVault__secret = "silver"
          __init__: Vault.__init__ (owner, _Vault__pin = 1234), then _SubVault__pin = 9999
          own_pin() reads self._SubVault__pin
bottom:   v.__pin is the plain name "__pin" -> does v have it?
```

`reveal` was written in `Vault`, so on a `SubVault` object it still reads `_Vault__...`.
