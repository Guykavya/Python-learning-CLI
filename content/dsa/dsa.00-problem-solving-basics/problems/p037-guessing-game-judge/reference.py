secret = int(input())
count = 0
while True:
    guess = int(input())
    if guess < 1 or guess > 100:
        print("out of range")
        continue
    count += 1
    if guess < secret:
        print("higher")
    elif guess > secret:
        print("lower")
    else:
        print(f"correct in {count} guesses")
        break
