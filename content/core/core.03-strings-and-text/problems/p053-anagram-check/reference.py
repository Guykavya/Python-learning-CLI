import string

table = str.maketrans("", "", string.punctuation + string.whitespace)
key1 = "".join(sorted(input().casefold().translate(table)))
key2 = "".join(sorted(input().casefold().translate(table)))
print(f"Key 1: {key1}")
print(f"Key 2: {key2}")
print(f"Anagrams: {key1 == key2}")
