start_text = input().strip()
end_text = input().strip()
length = int(input())

start = int(start_text[:2]) * 60 + int(start_text[3:])
end = int(end_text[:2]) * 60 + int(end_text[3:])

if length <= 0:
    print("invalid length")
else:
    found = False
    for s in range(start, end - length + 1, length):
        h1, m1 = divmod(s, 60)
        h2, m2 = divmod(s + length, 60)
        print(f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}")
        found = True
    if not found:
        print("No slots")
