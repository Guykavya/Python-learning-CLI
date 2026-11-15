class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_list(head):
    prev = None
    cur = head
    while cur is not None:
        nxt = cur.next          # 1. save the rest of the list
        cur.next = prev         # 2. flip the arrow
        prev = cur              # 3. the reversed part now starts at cur
        cur = nxt               # 4. move on
    return prev
