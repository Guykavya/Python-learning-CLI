amount = float(eval(input()))
have = int(input())
want = int(input())
scaled = amount * want / have
print(f"Cups: {scaled}")
print(f"About: {scaled:.3f}")
