name = input()
head, dot, tail = name.rpartition(".")
print(f"Name: {head or tail}")
print(f"Extension: {(dot and tail).lower() or '(none)'}")
