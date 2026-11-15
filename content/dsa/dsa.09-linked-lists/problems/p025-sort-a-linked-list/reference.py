class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def merge_two(a, b):
    dummy = ListNode()
    tail = dummy
    while a is not None and b is not None:
        if b.val < a.val:                    # ties: a first, so the sort is stable
            tail.next = b
            b = b.next
        else:
            tail.next = a
            a = a.next
        tail = tail.next
    tail.next = a if a is not None else b
    return dummy.next


def sort_list(head):
    if head is None or head.next is None:
        return head
    slow, fast = head, head.next             # slow stops at the end of the first half
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None                         # cut the list in two
    return merge_two(sort_list(head), sort_list(second))
