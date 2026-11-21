## Approach

The model answer is in `answer.md`. The argument has one root: a function that takes values and returns values can be called by **anyone**: a test, argparse, Click, Typer, a scheduled job. A command that reads the command line and prints can be called only from a terminal (or something pretending to be one).

## Cost

A thin layer means two files instead of one and a few more names. For a 20-line throwaway script that is not worth it; for anything you run weekly, test, or schedule, it pays back the first time you change the tool.

## Another way

Look at your own scripts: for each, count how many lines inside the command function do something other than parse, call and print. If that number is large, move those lines into a function, write one test for it, and point the command at it. Repeat until the command is boring.
