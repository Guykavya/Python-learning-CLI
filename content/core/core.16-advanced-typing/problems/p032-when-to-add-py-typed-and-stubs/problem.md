# Explain: py.typed, stubs and untyped libraries

Three situations:

1. **Meera** writes a small library `textkit` with full type hints and publishes it. Users run mypy
   on code that imports it, but mypy says
   `Skipping analyzing "textkit": module is installed, but missing library stubs or py.typed marker`.
2. **Karan** uses the old library `oldlib`, which has no hints at all. His mypy run says
   `Cannot find implementation or library stub for module named "oldlib"`. A `types-requests`
   package exists for another library he uses, `requests`, and he wonders what that is.
3. **Isha** has a 12,000-line project and wants typing, but turning on `strict = true` produces
   thousands of errors.

In `answer.md` (about 200 to 350 words), explain:

1. What must Meera add to her package, and what does it tell mypy? Where must it be placed?
2. What are the options for Karan with `oldlib` (at least two), and what is a `types-requests`
   package? What does mypy do if he silences the missing import for `oldlib` without writing a stub?
3. When would you write your own `.pyi` stub, and when would you rather annotate the source?
4. What would you advise Isha: how to move to typing a big project step by step?

See the model answer shown when you check.
