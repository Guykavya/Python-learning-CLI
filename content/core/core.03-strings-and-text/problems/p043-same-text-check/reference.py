import unicodedata

a = input()
b = input()
na = unicodedata.normalize("NFC", a).casefold()
nb = unicodedata.normalize("NFC", b).casefold()
print(f"Exact: {a == b}")
print(f"Ignoring case: {a.casefold() == b.casefold()}")
print(f"Normalised: {na == nb}")
print(f"Lengths: {len(a)} {len(b)}")
