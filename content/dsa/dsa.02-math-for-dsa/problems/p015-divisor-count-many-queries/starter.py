import sys

data = sys.stdin.read().split()
q = int(data[0])
queries = [int(x) for x in data[1:1 + q]]
# TODO: build the smallest-prime-factor table once, up to max(queries), then factorise each query with it
for n in queries:
    print(1)
