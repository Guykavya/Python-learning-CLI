k = int(input())

# Step 1: skip whole blocks of numbers with the same number of digits.
length = 1      # digits per number in the current block
count = 9       # how many numbers have this many digits (9, 90, 900, ...)
start = 1       # the first number in the block (1, 10, 100, ...)
while k > length * count:
    k -= length * count
    length += 1
    count *= 10
    start *= 10

# Step 2: k is now a position inside this block (1-based).
number = start + (k - 1) // length     # which number holds the digit
index = (k - 1) % length               # which digit of it, 0 = leftmost

# Step 3: drop the digits to the right of the one we want, then take the last digit.
drop = length - 1 - index
while drop > 0:
    number //= 10
    drop -= 1
print(number % 10)
