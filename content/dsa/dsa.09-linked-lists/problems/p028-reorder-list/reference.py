class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reorder_list(head):
    if head is None or head.next is None:
        return None
    slow, fast = head, head.next
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                     # cut: the first half ends at slow
    prev = None                          # reverse the second half
    while second is not None:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt
    first, second = head, prev
    while second is not None:            # weave: first, last, second, second-last, ...
        n1 = first.next
        n2 = second.next
        first.next = second
        second.next = n1
        first = n1
        second = n2
    return None
