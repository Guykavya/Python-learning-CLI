x = int(input())
if x % 1111 == 0:
    print("invalid")
else:
    steps = 0
    while True:
        big = 0
        small = 0
        place = 1
        for d in range(9, -1, -1):
            # How many times does digit d appear among the 4 digits of x?
            count = 0
            m = x
            for k in range(4):
                if m % 10 == d:
                    count += 1
                m //= 10
            # Use digit d that many times.
            for k in range(count):
                big = big * 10 + d          # add d on the right of big
                small = small + d * place   # add d on the left of small
                place *= 10
        diff = big - small
        steps += 1
        print(f"{big:04d} - {small:04d} = {diff:04d}")
        x = diff
        if diff == 6174:
            break
    print(f"steps {steps}")
