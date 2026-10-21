marks = int(input())
total = int(input())
pct = marks / total * 100
print(f"Percentage: {pct:.2f}")
print("Passed:", pct > 40)
print("Distinction:", pct >= 75)
print("Valid:", marks >= 0)
