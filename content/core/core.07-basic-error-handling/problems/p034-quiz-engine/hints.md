## Hint 1

Make a list of every exception that can happen and decide who handles it:
bad question data (`check_questions` raises; nobody catches it: the author must fix the data),
bad answers (`interpret` raises; the asking loop catches it and asks again), stopping
(`ask` raises `EOFError`/`KeyboardInterrupt`; `run_quiz` catches them once, around the whole loop).

## Hint 2

A helper `ask_until_valid(question, ask, tell)` with `while True`, a `try` around `interpret`,
and `return` on success keeps `run_quiz` short. Keep `ask(...)` **outside** that `try`: its
exceptions are not "invalid answers".

## Hint 3

```
check_questions(questions)
score = 0
try:
    for n, question in enumerate(questions, start=1):
        tell the prompt (and options)
        value = ask_until_valid(question, ask, tell)
        if is_correct(...): score += 1; tell("Correct!")
        else: tell(f"Not quite. The answer is {question['answer']}.")
except (EOFError, KeyboardInterrupt):
    tell("Quiz stopped.")
finally:
    tell(f"Score: {score}/{len(questions)}")
return score
```
