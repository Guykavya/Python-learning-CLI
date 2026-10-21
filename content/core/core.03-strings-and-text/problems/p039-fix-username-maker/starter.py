# Username maker (buggy). Fix it so it matches the specification in problem.md.
name = input().strip()
year = input()
words = name.split(" ")
first = words[0]
last = words[1]
first.lower()
username = first + last[0] + year[:-2]
print("Hello, " + name.title() + "!")
print("Username: " + username)
print("Age in 2026: " + 2026 - int(year))
