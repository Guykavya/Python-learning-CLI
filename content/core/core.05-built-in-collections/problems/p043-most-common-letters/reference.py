counts = {}
for ch in input().lower():
    if ch.isalpha():
        counts[ch] = counts.get(ch, 0) + 1
top = sorted((-n, ch) for ch, n in counts.items())[:3]
if not top:
    print("No letters")
for neg, ch in top:
    print(f"{ch}: {-neg}")
