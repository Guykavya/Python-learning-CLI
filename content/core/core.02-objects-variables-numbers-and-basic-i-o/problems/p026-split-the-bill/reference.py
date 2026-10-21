from decimal import Decimal

total = Decimal(input())
people = int(input())
paise = int(total * 100)
share, left = divmod(paise, people)
print(f"Each pays: {share // 100}.{share % 100:02d}")
print(f"Left over paise: {left}")
