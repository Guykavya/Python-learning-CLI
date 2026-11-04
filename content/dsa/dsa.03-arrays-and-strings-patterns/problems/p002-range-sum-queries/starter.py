n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
# TODO: build prefix sums once, then answer each question with p[r] - p[l - 1]
for _ in range(q):
    l, r = map(int, input().split())
    print(0)
