q = int(input())
m = int(input())
year = int(input())
early = (14 - m) // 12          # 1 for January and February, 0 otherwise
y = year - early
m = m + 12 * early
K = y % 100
J = y // 100
h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7
print((h + 5) % 7 + 1)
