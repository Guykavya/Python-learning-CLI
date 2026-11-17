def sift_up(a, i):
    while i > 0:
        p = (i - 1) // 2
        if a[i] < a[p]:
            a[i], a[p] = a[p], a[i]
            i = p
        else:
            break
