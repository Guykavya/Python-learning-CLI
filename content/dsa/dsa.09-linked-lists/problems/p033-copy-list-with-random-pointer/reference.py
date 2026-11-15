class RNode:
    def __init__(self, val, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random


def copy_random_list(head):
    if head is None:
        return None
    cur = head                               # 1. weave: A -> A' -> B -> B' -> ...
    while cur is not None:
        cur.next = RNode(cur.val, cur.next)
        cur = cur.next.next
    cur = head                               # 2. randoms: the copy of X.random is X.random.next
    while cur is not None:
        if cur.random is not None:
            cur.next.random = cur.random.next
        cur = cur.next.next
    new_head = head.next                     # 3. unweave and restore the original list
    cur = head
    while cur is not None:
        copy = cur.next
        cur.next = copy.next
        copy.next = copy.next.next if copy.next is not None else None
        cur = cur.next
    return new_head
