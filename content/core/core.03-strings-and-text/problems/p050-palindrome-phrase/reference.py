import string

table = str.maketrans("", "", string.punctuation + string.whitespace)
cleaned = input().translate(table).casefold()
print(f"Cleaned: {cleaned}")
print(f"Palindrome: {cleaned == cleaned[::-1]}")
