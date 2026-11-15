def digit_square_sum(n):
    total = 0
    while n > 0:
        n, d = divmod(n, 10)
        total += d * d
    return total


def is_happy(n):
    slow = n
    fast = digit_square_sum(n)
    while fast != 1 and slow != fast:
        slow = digit_square_sum(slow)                     # one step
        fast = digit_square_sum(digit_square_sum(fast))   # two steps
    return fast == 1
