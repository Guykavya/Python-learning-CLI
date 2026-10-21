a = int(input())
b = int(input())
c = int(input())

largest = max(a, b, c)
others = a + b + c - largest

if a <= 0 or b <= 0 or c <= 0 or largest >= others:
    print("invalid")
else:
    if a == b == c:
        print("equilateral")
    elif a == b or b == c or a == c:
        print("isosceles")
    else:
        print("scalene")

    # right angle: largest^2 equals the sum of the other two squares
    if a * a + b * b + c * c - largest * largest == largest * largest:
        print("right")
    else:
        print("not right")
