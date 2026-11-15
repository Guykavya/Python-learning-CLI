n = int(input())
students = []
for _ in range(n):
    name, score = input().split()
    students.append((name, int(score)))
students.sort(key=lambda s: (-s[1], s[0]))
for name, score in students:
    print(name, score)
