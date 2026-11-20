q = int(input())
queue = []
for _ in range(q):
    parts = input().split()
    if parts[0] == "push":
        queue.append(int(parts[1]))
    elif parts[0] == "pop":
        if queue:
            print(queue.pop(0))
        else:
            print("empty")
    else:
        print(len(queue))
