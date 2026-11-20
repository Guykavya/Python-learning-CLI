import sys

data = sys.stdin.read().split()
n = int(data[0])
out = [str(int(x) ** 2) for x in data[1:1 + n]]
sys.stdout.write("\n".join(out) + "\n")
