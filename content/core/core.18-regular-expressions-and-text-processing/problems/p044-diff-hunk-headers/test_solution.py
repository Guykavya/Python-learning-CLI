from solution import parse_hunks

DIFF = """diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 import sys
+import os
 print("hi")
@@ -10 +11,2 @@ def main():
-    pass
+    run()
+    stop()
"""


def test_example():
    assert parse_hunks(DIFF) == [(1, 3, 1, 4), (10, 1, 11, 2)], "Find every header line, convert the numbers with int(), and use 1 for a missing length."


def test_values_are_ints():
    got = parse_hunks("@@ -1,2 +3,4 @@\n")
    assert got == [(1, 2, 3, 4)], "Four numbers in the order old_start, old_len, new_start, new_len."
    assert all(isinstance(v, int) for v in got[0]), "Convert the groups to int: groups are always strings."


def test_missing_lengths_default_to_one():
    assert parse_hunks("@@ -5 +5,2 @@\n") == [(5, 1, 5, 2)], "No ',B' means old_len 1. Make ',B' an optional group and test it with 'is None'."
    assert parse_hunks("@@ -7,3 +8 @@\n") == [(7, 3, 8, 1)], "No ',D' means new_len 1."
    assert parse_hunks("@@ -4 +4 @@\n") == [(4, 1, 4, 1)], "Both lengths missing: both are 1."


def test_zero_lengths_are_kept():
    assert parse_hunks("@@ -0,0 +1,3 @@\n") == [(0, 0, 1, 3)], "A length of 0 (a new file) is real, not missing. Test the group with 'is None'; never turn int 0 into 1 (for example with 'int(x) or 1')."


def test_header_must_start_the_line():
    text = "@@ -1 +1 @@\n-@@ -9 +9 @@\n @@ -8 +8 @@\n+@@ -7 +7 @@\nx @@ -6 +6 @@\n"
    assert parse_hunks(text) == [(1, 1, 1, 1)], "Only lines that START with '@@ -' are headers. Use ^ with re.MULTILINE (so ^ matches at the start of every line)."


def test_headers_on_later_lines():
    text = "intro\n@@ -2 +2 @@\nbody\n@@ -20,5 +21,6 @@ heading\n"
    assert parse_hunks(text) == [(2, 1, 2, 1), (20, 5, 21, 6)], "Headers are not on the first line. Without re.MULTILINE, ^ only matches at the very start of the text."


def test_malformed_headers_skipped():
    text = "@@ -a,1 +1 @@\n@@ -1,2 @@\n@@ -1 +x @@\n@@ -3 +3 @@\n"
    assert parse_hunks(text) == [(3, 1, 3, 1)], "Malformed lines are skipped: the numbers must be \\d+ and both - and + parts are required."


def test_no_trailing_newline_and_empty():
    assert parse_hunks("@@ -1 +1 @@") == [(1, 1, 1, 1)], "The last line may have no newline."
    assert parse_hunks("") == [], "No text, no hunks."


def test_big_numbers():
    assert parse_hunks("@@ -1200,15 +1250,0 @@\n") == [(1200, 15, 1250, 0)], "Numbers can have many digits: \\d+ not \\d."
