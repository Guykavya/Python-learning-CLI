## Approach

The design is a map of **who raises what, and who catches it**:

| Exception | Raised by | Caught by | Response |
|---|---|---|---|
| `ValueError` (bad data) | `check_questions` | nobody | the program stops before the first question with a precise message for the author |
| `ValueError` (bad answer) | `interpret` | `ask_until_valid` | tell the message, ask again |
| `EOFError`, `KeyboardInterrupt` | `ask` | `run_quiz`, around the whole loop | "Quiz stopped." |
| anything else | a bug | nobody | crashes, after `finally` showed the score |

Each `try` is narrow: `interpret` wraps only `int(...)`; `ask_until_valid` wraps only the call to
`interpret`; `run_quiz`'s `try` must cover the whole loop because stopping can happen at any
question. `finally` guarantees the score line on every exit, including the bug case. Validation of
the data happens before the `try`, so bad data never prints a score at all.

## Code

```python
KINDS = ("int", "text", "choice")


def check_questions(questions):
    """Raise ValueError('question N: ...') for the first problem in the question data."""
    if not questions:
        raise ValueError("the quiz has no questions")
    for n, q in enumerate(questions, start=1):
        for key in ("prompt", "answer", "kind"):
            if key not in q:
                raise ValueError(f"question {n}: missing {key!r}")
        kind, answer = q["kind"], q["answer"]
        if kind not in KINDS:
            raise ValueError(f"question {n}: unknown kind {kind!r}; use int, text or choice")
        if kind == "int":
            try:
                int(answer)
            except ValueError:
                raise ValueError(f"question {n}: answer {answer!r} is not a whole number") from None
        if kind == "choice":
            options = q.get("options")
            if not isinstance(options, list) or len(options) < 2:
                raise ValueError(f"question {n}: a choice question needs at least 2 options")
            if answer not in options:
                raise ValueError(f"question {n}: answer {answer!r} is not one of the options")


def interpret(question, text):
    """Convert the user's text for this question, or raise ValueError telling them what to type."""
    kind = question["kind"]
    if kind == "int":
        try:
            return int(text)
        except ValueError:
            raise ValueError("Please type a whole number, like 42.") from None
    if kind == "text":
        value = text.strip().lower()
        if not value:
            raise ValueError("Please type an answer.")
        return value
    options = question["options"]
    message = f"Please type a number from 1 to {len(options)}."
    try:
        number = int(text)
    except ValueError:
        raise ValueError(message) from None
    if not 1 <= number <= len(options):
        raise ValueError(message)
    return options[number - 1]


def is_correct(question, value):
    """Return True if the interpreted value is the right answer."""
    kind, answer = question["kind"], question["answer"]
    if kind == "int":
        return value == int(answer)
    if kind == "text":
        return value == answer.strip().lower()
    return value == answer


def ask_until_valid(question, ask, tell):
    """Ask until interpret() accepts the answer; return the interpreted value."""
    while True:
        text = ask("> ")
        try:
            return interpret(question, text)
        except ValueError as e:
            tell(str(e))


def run_quiz(questions, ask=input, tell=print):
    """Run the quiz, never crashing on user input. Return the score."""
    check_questions(questions)
    score = 0
    try:
        for n, question in enumerate(questions, start=1):
            tell(f"Q{n}. {question['prompt']}")
            if question["kind"] == "choice":
                for i, option in enumerate(question["options"], start=1):
                    tell(f"  {i}) {option}")
            value = ask_until_valid(question, ask, tell)
            if is_correct(question, value):
                score += 1
                tell("Correct!")
            else:
                tell(f"Not quite. The answer is {question['answer']}.")
    except (EOFError, KeyboardInterrupt):
        tell("Quiz stopped.")
    finally:
        tell(f"Score: {score}/{len(questions)}")
    return score
```

## Complexity

O(q + a) for q questions and a answers typed (each check is constant work for short text).

## Another way

`interpret` could return `None` for an invalid answer instead of raising. Then the loop must
check for `None`, and the "what to type" message has to live in the loop rather than next to the
rule it explains. Raising keeps each message beside its rule and makes the "invalid answer" path
impossible to forget. For the real project, wrap `main()` once more at the very top: `run_quiz`
already handles the user stopping, so the top level only needs to turn a data `ValueError` into a
friendly "the quiz file is broken: ..." message.
