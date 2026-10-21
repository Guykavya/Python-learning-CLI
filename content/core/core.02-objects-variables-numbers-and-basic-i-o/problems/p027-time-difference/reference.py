sh = int(input())
sm = int(input())
eh = int(input())
em = int(input())
diff = ((eh * 60 + em) - (sh * 60 + sm)) % 1440
hours, minutes = divmod(diff, 60)
print(f"{hours} h {minutes} min")
