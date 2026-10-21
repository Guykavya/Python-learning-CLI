n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

count = {}                      # code -> how many times it appears in the current block
for x in a[:k]:
    count[x] = count.get(x, 0) + 1
answers = [len(count)]

for i in range(k, n):
    entering = a[i]
    leaving = a[i - k]
    count[entering] = count.get(entering, 0) + 1
    count[leaving] -= 1
    if count[leaving] == 0:
        del count[leaving]      # only codes still in the block may stay in the dict
    answers.append(len(count))

print(" ".join(str(x) for x in answers))
