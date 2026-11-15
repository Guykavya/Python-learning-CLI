class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def get_intersection(a, b):
    p, q = a, b
    while p is not q:
        p = p.next if p is not None else b       # at the end, switch to the other list
        q = q.next if q is not None else a
    return p                                     # the shared node, or None
