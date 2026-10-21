words = input().split()
target = input().strip()
kept = [w for w in words if w != target]
print(" ".join(kept) if kept else "(empty)")
print("Removed:", len(words) - len(kept))
