text = input()
letter = input()
print(f"Exact: {text.count(letter)}")
print(f"Any case: {text.casefold().count(letter.casefold())}")
