class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def reverse_list(head):
    prev = None
    while head is not None:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev


def is_palindrome(head):
    if head is None or head.next is None:
        return True
    slow, fast = head, head.next             # slow stops at the end of the first half
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    second = reverse_list(slow.next)         # reverse the second half
    a, b = head, second
    result = True
    while b is not None:                     # the second half is not longer than the first
        if a.val != b.val:
            result = False
            break
        a = a.next
        b = b.next
    slow.next = reverse_list(second)         # restore the list
    return result
