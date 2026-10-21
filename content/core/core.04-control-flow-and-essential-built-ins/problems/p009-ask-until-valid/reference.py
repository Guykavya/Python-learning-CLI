attempts = 0
while True:
    text = input().strip()
    attempts += 1
    if text.isdigit() and 1 <= int(text) <= 10:
        break
    print(f"Invalid: {text}")
word = "attempt" if attempts == 1 else "attempts"
print(f"Accepted {int(text)} after {attempts} {word}")
