import string

table = str.maketrans("", "", string.punctuation)
words = input().translate(table).casefold().split()
print(f"Words: {len(words)}")
print(" ".join(words))
