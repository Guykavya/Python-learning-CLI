import string

text = input()
target = input().strip().casefold()
table = str.maketrans("", "", string.punctuation)
words = text.translate(table).casefold().split()
n = len(words)
safe = max(n, 1)
average = len("".join(words)) / safe
longest = max(words, key=len, default="-")
count = words.count(target)

print("Text statistics")
print("=" * 26)
print(f"{'Characters':<16}{len(text):>10,}")
print(f"{'Non-space':<16}{len(''.join(text.split())):>10,}")
print(f"{'Words':<16}{n:>10,}")
print(f"{'Average length':<16}{average:>10.2f}")
print(f"{'Longest word':<16}{longest:>10}")
print(f"{'Target word':<16}{target:>10}")
print(f"{'Target count':<16}{count:>10,}")
print(f"{'Target share':<16}{count / safe:>10.1%}")
