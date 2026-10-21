queue = []
while True:
    parts = input().split()
    match parts:
        case ["end"]:
            break
        case ["join", name]:
            if name in queue:
                print(f"{name} is already in the queue")
            else:
                queue.append(name)
        case ["serve"]:
            if queue:
                print("Serving", queue.pop(0))
            else:
                print("Nobody to serve")
        case ["leave", name]:
            if name in queue:
                queue.remove(name)
            else:
                print(f"{name} is not in the queue")
        case ["show"]:
            print("Queue:", " ".join(queue) if queue else "(empty)")
