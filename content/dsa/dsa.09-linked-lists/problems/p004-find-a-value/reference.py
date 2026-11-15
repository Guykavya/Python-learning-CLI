class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def find(head, target):
    index = 0
    cur = head
    while cur is not None:
        if cur.val == target:
            return index
        index += 1
        cur = cur.next
    return -1
