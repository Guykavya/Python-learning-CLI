items = input().split()
k = int(input())
chunks = [items[s:s + k] for s in range(0, len(items), k)]
if not chunks:
    print("No chunks")
for i, chunk in enumerate(chunks, start=1):
    print(f"{i}: {' '.join(chunk)}")
