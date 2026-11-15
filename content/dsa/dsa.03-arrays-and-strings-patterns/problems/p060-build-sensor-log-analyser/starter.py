# Sensor log analyser: read n readings, then q commands, and print one line per command.
# See problem.md for the six commands and the error rules.
# Plan: build prefix sums once; one function per command returning a string; a dispatcher that validates each line.
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
for _ in range(q):
    line = input()
    print("error")
