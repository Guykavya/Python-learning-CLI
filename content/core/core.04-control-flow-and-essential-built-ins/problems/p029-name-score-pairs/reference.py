names = input().split()
scores = input().split()
if len(names) != len(scores):
    print(f"Mismatch: {len(names)} names, {len(scores)} scores")
elif not names:
    print("No data")
else:
    total = 0
    for name, score in zip(names, scores):
        print(f"{name}: {score}")
        total += int(score)
    print(f"Average: {total / len(names):.1f}")
