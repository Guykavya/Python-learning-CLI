import sys

data = sys.stdin.read().split()
q = int(data[0])
queries = [int(x) for x in data[1:1 + q]]
# TODO: sieve ONCE up to max(queries), build count[k] = number of primes <= k, then answer each query.
for n in queries:
    print(0)
