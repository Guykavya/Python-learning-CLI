# A number theory toolkit: read commands, one per line, and print one result line per command.
# Line 1 is k, the number of commands. See problem.md for the commands and the exact output formats.
# Plan: write one small function per command, then a loop that reads a line, splits it, and calls the right function.
k = int(input())
for _ in range(k):
    line = input()
    print("error")
