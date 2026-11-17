def heap_sort(a, reverse=False):
    n = len(a)

    def sift_down(i, end):
        while True:
            top = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < end and (a[c] < a[top] if reverse else a[top] < a[c]):
                    top = c
            if top == i:
                return
            a[i], a[top] = a[top], a[i]
            i = top

    for i in range(n // 2 - 1, -1, -1):      # phase 1: build the heap
        sift_down(i, n)
    for end in range(n - 1, 0, -1):          # phase 2: move the root behind the heap
        a[0], a[end] = a[end], a[0]
        sift_down(0, end)
