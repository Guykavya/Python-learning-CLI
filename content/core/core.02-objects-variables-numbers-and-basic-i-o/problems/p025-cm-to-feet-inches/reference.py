cm = float(input())
total_inches = round(cm / 2.54)
feet, inches = divmod(total_inches, 12)
print(f"{feet} ft {inches} in")
