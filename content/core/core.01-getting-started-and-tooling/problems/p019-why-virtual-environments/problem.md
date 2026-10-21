# Why virtual environments?

Answer in `answer.md`, in your own words, as if explaining to a classmate who
has never used one.

1. What problem does a virtual environment solve? Give a concrete example with
   two projects.
2. List the exact terminal commands to create a venv in a project, activate it,
   install the package `requests`, save the installed versions to a file, and
   run `app.py`.
3. What is actually inside the `.venv` folder? What does `source
   .venv/bin/activate` change, and why is activating optional?
4. Why is `python -m pip install ...` safer than `pip install ...`?
5. Should `.venv` be committed to Git? What do you commit instead?
6. A friend says: "I ran `pip install requests`, but `python3 app.py` says
   `ModuleNotFoundError: No module named 'requests'`." Give two likely causes
   and the commands you would use to check.
