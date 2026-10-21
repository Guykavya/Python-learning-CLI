import textwrap

width = int(input())
text = input()
print(textwrap.fill(text, width))
print("-" * width)
print(textwrap.shorten(text, width, placeholder=" ..."))
