# Build: a quiz engine that never crashes

This is the assessed build for this module and the core of the module project. Build a small quiz
engine from four functions. Questions are dicts:

```python
{"prompt": "7 x 8?", "answer": "56", "kind": "int"}
{"prompt": "Capital of Kerala?", "answer": "Thiruvananthapuram", "kind": "text"}
{"prompt": "Which is a list?", "answer": "[1, 2]", "kind": "choice", "options": ["(1, 2)", "[1, 2]", "{1, 2}"]}
```

### 1. `check_questions(questions)`

The question data is written by the quiz **author**. Bad data must stop the program before the
first question, with a precise message. Raise `ValueError` for the first problem found (number
questions from 1):

| Problem | Message |
|---|---|
| empty list | `the quiz has no questions` |
| a missing key (check `prompt`, `answer`, `kind` in that order) | `question <n>: missing <key!r>` |
| `kind` not `int`, `text` or `choice` | `question <n>: unknown kind <kind!r>; use int, text or choice` |
| `int` question whose answer `int()` cannot convert | `question <n>: answer <answer!r> is not a whole number` |
| `choice` question without an `options` list of at least 2 items | `question <n>: a choice question needs at least 2 options` |
| `choice` answer not in its options | `question <n>: answer <answer!r> is not one of the options` |

### 2. `interpret(question, text)`

Turn what the user typed into a value, or raise `ValueError` with a message telling them what to
type (these messages are shown to the user):

- `int`: `int(text)`; on failure `Please type a whole number, like 42.`
- `text`: `text.strip().lower()`; if that is empty, `Please type an answer.`
- `choice`: the user types an option's **number**, from 1; return that option. Anything else
  (not a number, or out of range) gives `Please type a number from 1 to <number of options>.`

### 3. `is_correct(question, value)`

`True` if the interpreted `value` is right: for `int`, `value == int(answer)`; for `text`,
`value == answer.strip().lower()`; for `choice`, `value == answer`.

### 4. `run_quiz(questions, ask=input, tell=print)`

1. Call `check_questions` first. If it raises, nothing is asked and the exception propagates.
2. For each question `n` (from 1): `tell(f"Q{n}. {prompt}")`; for a choice question, also
   `tell(f"  {i}) {option}")` for each option, numbered from 1.
3. Read answers with `ask("> ")`. While `interpret` raises `ValueError`, `tell` its message and
   ask again. An invalid answer is **not** counted as wrong.
4. Then `tell("Correct!")` and add 1 to the score, or `tell(f"Not quite. The answer is {answer}.")`.
5. If `ask` raises `EOFError` or `KeyboardInterrupt` (the user wants to stop), `tell("Quiz stopped.")`
   and stop asking.
6. **Always**, as the very last message, `tell(f"Score: {score}/{number of questions}")`. Use
   `finally`.
7. Return the score.

No bare `except` and no `except Exception` anywhere.

**Example**

```python
questions = [{"prompt": "7 x 8?", "answer": "56", "kind": "int"},
             {"prompt": "Which is a list?", "answer": "[1, 2]", "kind": "choice",
              "options": ["(1, 2)", "[1, 2]"]}]
answers = iter(["fifty-six", "56", "3", "1"])
messages = []
run_quiz(questions, ask=lambda prompt: next(answers), tell=messages.append)   # 1
messages
# ['Q1. 7 x 8?', 'Please type a whole number, like 42.', 'Correct!',
#  'Q2. Which is a list?', '  1) (1, 2)', '  2) [1, 2]',
#  'Please type a number from 1 to 2.', 'Not quite. The answer is [1, 2].',
#  'Score: 1/2']
```

Be ready to explain, for each function, which exceptions it can raise and where each one is
caught.
