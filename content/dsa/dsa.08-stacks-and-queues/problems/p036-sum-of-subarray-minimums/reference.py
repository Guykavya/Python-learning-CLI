MOD = 10 ** 9 + 7


def sum_subarray_mins(arr):
    n = len(arr)
    prev = [-1] * n
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)

    nxt = [n] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)

    total = 0
    for i in range(n):
        total += arr[i] * (i - prev[i]) * (nxt[i] - i)
    return total % MOD
