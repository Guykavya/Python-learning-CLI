name = input()
message = "Hello, " + name + "!"
width = len(message) + 2

border = "+" + "-" * width + "+"
empty = "|" + " " * width + "|"
print(border)
print(empty)
print("| " + message + " |")
print(empty)
print(border)
