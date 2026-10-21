start = int(input())
stop = int(input())
step = int(input())
if step == 0:
    print("step cannot be 0")
else:
    r = range(start, stop, step)
    if r:
        line = ""
        for n in r:
            line += str(n) + " "
        print(line.strip())
    else:
        print("(empty)")
    print(f"Count: {len(r)}")
