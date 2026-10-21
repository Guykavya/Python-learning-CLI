marks = int(input())
total = int(input())
pct = marks / total * 100
print(f"Percentage: {pct:.2f}")
print("Passed:", pct >= 40)
print("Distinction:", 75 <= pct <= 100)
print("Valid:", 0 <= marks <= total)
