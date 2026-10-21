done = int(input())
total = int(input())
filled = done * 20 // total
bar = "#" * filled + "-" * (20 - filled)
print(f"[{bar}] {done / total:.0%} ({done}/{total})")
