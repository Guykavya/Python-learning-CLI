def is_pal(s):
    # TODO: two pointers; skip non-alphanumeric characters; compare lowercased characters
    return True


t = int(input())
for _ in range(t):
    print("yes" if is_pal(input()) else "no")
