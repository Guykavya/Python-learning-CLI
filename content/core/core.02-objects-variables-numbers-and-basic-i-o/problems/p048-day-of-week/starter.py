q = int(input())
m = int(input())
year = int(input())
K = year % 100
J = year // 100
h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7
print(h)
