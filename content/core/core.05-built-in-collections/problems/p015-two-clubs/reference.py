python = set(input().split())
chess = set(input().split())
for label, group in [("Both", python & chess), ("Only Python", python - chess),
                     ("Only Chess", chess - python), ("Either", python | chess)]:
    print(f"{label}: {' '.join(sorted(group)) if group else '-'}")
