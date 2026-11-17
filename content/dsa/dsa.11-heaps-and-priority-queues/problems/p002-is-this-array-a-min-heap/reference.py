def is_min_heap(a):
    for i in range(1, len(a)):
        if a[i] < a[(i - 1) // 2]:
            return False
    return True
