day = int(input())
month = int(input())
year = int(input())

leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

if month < 1 or month > 12:
    print("invalid date")
else:
    if month == 2:
        if leap:
            length = 29
        else:
            length = 28
    elif month == 4 or month == 6 or month == 9 or month == 11:
        length = 30
    else:
        length = 31

    if day < 1 or day > length:
        print("invalid date")
    else:
        # Zeller: January and February count as months 13 and 14 of the previous year.
        m = month
        y = year
        if m < 3:
            m += 12
            y -= 1
        k = y % 100
        j = y // 100
        h = (day + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
        if h == 0:
            print("Saturday")
        elif h == 1:
            print("Sunday")
        elif h == 2:
            print("Monday")
        elif h == 3:
            print("Tuesday")
        elif h == 4:
            print("Wednesday")
        elif h == 5:
            print("Thursday")
        else:
            print("Friday")
