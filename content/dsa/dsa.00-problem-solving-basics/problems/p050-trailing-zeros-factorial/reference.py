n = int(input())

# Each trailing zero needs a 2 and a 5. There are always more 2s, so count the 5s.
count = 0
power = 5
while power <= n:
    count += n // power   # numbers up to n that contain this power of 5
    power *= 5
print(count)
