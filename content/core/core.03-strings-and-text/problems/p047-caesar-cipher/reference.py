import string

k = int(input()) % 26
lower = string.ascii_lowercase
upper = string.ascii_uppercase
table = str.maketrans(lower + upper, lower[k:] + lower[:k] + upper[k:] + upper[:k])
print(input().translate(table))
