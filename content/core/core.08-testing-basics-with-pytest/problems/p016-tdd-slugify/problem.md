# TDD: grow slugify one test at a time

A *slug* is the part of a web address made from a title: `"Hello, World!"` becomes
`"hello-world"`. The tests in `test_solution.py` are ordered like a TDD session: each test
adds **one** new rule. Work like this (chapter section 14):

1. Run the tests. The first one is red (failing).
2. Write the smallest code that makes that test pass.
3. Run again. The next test is red. Repeat.
4. When everything is green, tidy the code and run once more.

The rules, in the order the tests introduce them:

1. letters become lower case;
2. words are joined with a single `-`;
3. extra spaces anywhere (before, after, between words) are ignored;
4. only letters and digits are kept inside a word, other characters are dropped (`"Hello, World!"`);
5. a word that becomes empty after dropping characters disappears (`"a - b"` is `"a-b"`);
6. empty text gives `""`.

**Examples**

```python
slugify("Hello World")        # "hello-world"
slugify("  Python   3.14 ")   # "python-314"
slugify("Rock & Roll!")       # "rock-roll"
```
