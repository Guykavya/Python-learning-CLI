s = input().strip()
t = input().strip()

need = {}
for ch in t:
    need[ch] = need.get(ch, 0) + 1

# TODO: grow `right`; when the window covers `need`, shrink `left` as far as possible and record the window.
print(-1)
