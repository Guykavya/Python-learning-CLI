total = int(input())
hours, rest = divmod(total, 3600)
minutes, seconds = divmod(rest, 60)
print(f"{hours}:{minutes:02d}:{seconds:02d}")
