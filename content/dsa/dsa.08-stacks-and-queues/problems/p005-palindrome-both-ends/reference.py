from collections import deque


def first_mismatch(text):
    d = deque(ch.lower() for ch in text if ch.isalnum())
    while len(d) > 1:
        left = d.popleft()
        right = d.pop()
        if left != right:
            return (left, right)
    return None
