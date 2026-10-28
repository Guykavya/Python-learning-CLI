**1. What a pickle is.** A pickle is not only data. It is a small program for a stack machine, a list of
instructions that tells Python how to rebuild the object. `pickle.load` does not just read values; it **runs**
those instructions. Some instructions mean "import this name and call it with these arguments".

**2. Why it is dangerous.** The instruction "call a function with these arguments" can name any function that
Python can import. A harmless example is a pickle that makes `load` call `print("hello")` or call
`list.append` on a list. An attacker can choose a harmful function instead, such as one that runs a shell
command or deletes files, and it runs with the rights of your program, as soon as you call `pickle.load`. You
cannot check the file first, because loading it is what runs the code. So "only data" is false, and an uploaded
pickle is the same as an uploaded program that you run.

**3. json is different.** `json` can only describe strings, numbers, booleans, null, lists and dicts. Reading it
never calls anything of the file's choosing. The price is that json cannot keep tuples (they become lists),
sets, bytes, or your own types, while `pickle` can keep almost any Python object, including those.

**4. Safe ways.** Use json (or csv, TOML) for data that comes from outside. Use pickle only for files that your
own program wrote and that nobody else can change, and if it has to travel, sign it with a secret key
(`hmac`) and check the signature **before** you call `load`.
