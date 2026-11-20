def tribonacci(n):
    a, b, c = 0, 1, 1            # T(i), T(i+1), T(i+2) with i = 0
    for _ in range(n):
        a, b, c = b, c, a + b + c
    return a
