text = input().strip()
if not text:
    print("(blank)")
else:
    shout = text.upper()
    print(shout if shout.endswith("!") else shout + "!")
