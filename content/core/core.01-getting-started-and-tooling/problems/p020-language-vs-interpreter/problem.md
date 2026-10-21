# Language, interpreter, bytecode

Answer in `answer.md`, in your own words:

1. What is the difference between "Python the language" and "CPython"? Name
   one other implementation and say what it is good for.
2. Describe the two stages CPython goes through when you run
   `python3 hello.py`. Use these words: source, compile, bytecode, evaluation
   loop.
3. A 30-line file has a missing bracket on line 30. Why does line 1's `print`
   produce no output? A different 30-line file has a typo `pirnt` on line 30.
   Why does line 1's `print` produce output this time?
4. What is the `__pycache__` folder and the `.pyc` files inside? Is it safe to
   delete them? Should they go in Git?
5. Explain the three parts of the version `3.14.4`. Why might code written for
   3.14 fail on 3.10, while code written for 3.10 usually works on 3.14?

Use small examples. The `dis` module (`import dis; dis.dis("x = 1 + 2")`) may
help you explore question 2.
