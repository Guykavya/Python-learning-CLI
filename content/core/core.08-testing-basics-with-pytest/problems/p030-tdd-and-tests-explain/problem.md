# Explain: test first, test after, and when tests mislead

In `answer.md` (about 200 to 350 words), discuss testing as a working method:

1. Describe the **red, green, refactor** loop in your own words, using the example of writing
   `slugify` (turning `"Hello World"` into `"hello-world"`). Why must the test fail first?
2. Give **two benefits** of writing the test before the code, and **one honest cost** or
   limitation of doing so.
3. A teammate writes the function first and "adds tests afterwards" by running the function,
   copying its output into `assert result == <that output>`. Explain why such a test is
   dangerous. Use the word **specification**.
4. Your tests all pass, but a user reports a bug. What do you do **first**, before fixing the
   code? Explain how this connects to **regression**.
5. Name two kinds of code or situations where writing automated tests is not worth the effort,
   or is not enough.
