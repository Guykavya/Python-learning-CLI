garbled = input()
fixed = garbled.encode("latin-1").decode("utf-8")
print(f"Fixed: {fixed}")
print(f"Shorter by: {len(garbled) - len(fixed)}")
