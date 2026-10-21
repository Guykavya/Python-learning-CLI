names = input().split()
if not names:
    print("No names")
else:
    print(f"First: {min(names, key=str.lower)}")
    print(f"Last: {max(names, key=str.lower)}")
    print(f"Longest: {max(names, key=len)}")
