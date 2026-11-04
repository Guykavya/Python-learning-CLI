q = int(input())
# TODO: handle q commands: "set key value time" and "get key time"
for _ in range(q):
    parts = input().split()
    if parts[0] == "get":
        print("NONE")
