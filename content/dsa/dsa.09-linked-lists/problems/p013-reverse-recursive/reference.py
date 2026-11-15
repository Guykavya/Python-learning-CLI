class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_rec(head):
    if head is None or head.next is None:      # 0 or 1 node: already reversed
        return head
    new_head = reverse_rec(head.next)          # reverse everything after head
    head.next.next = head                      # the old next now points back at head
    head.next = None                           # head becomes the tail
    return new_head
