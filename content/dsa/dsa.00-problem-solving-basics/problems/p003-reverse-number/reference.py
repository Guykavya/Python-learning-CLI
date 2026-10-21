n = int(input())
negative = n < 0
n = abs(n)
rev = 0
while n > 0:
    digit = n % 10
    rev = rev * 10 + digit
    n //= 10
if negative:
    rev = -rev
print(rev)
