n = int(input())
students = []
for _ in range(n):
    name, score = input().split()
    students.append((name, int(score)))
# TODO: sort by score (high to low), then name (A to Z), and print "name score" lines
for name, score in students:
    print(name, score)
