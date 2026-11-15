class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def length(head):
    count = 0
    cur = head
    while cur is not None:
        count += 1
        cur = cur.next
    return count


def get(head, k):
    if k < 0:
        return None
    cur = head
    for _ in range(k):
        if cur is None:
            return None
        cur = cur.next
    return cur
