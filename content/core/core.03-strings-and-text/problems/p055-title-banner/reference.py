import textwrap

title = input()
w = int(input())
inner = w - 4
text = textwrap.shorten(title, width=inner, placeholder="...")
edge = "+" + "-" * (w - 2) + "+"
print(edge)
print(f"| {text:^{inner}} |")
print(edge)
