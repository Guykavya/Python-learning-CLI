KINDS = ("int", "text", "choice")


def check_questions(questions):
    """Raise ValueError('question N: ...') for the first problem in the question data."""


def interpret(question, text):
    """Convert the user's text for this question, or raise ValueError telling them what to type."""
    return text


def is_correct(question, value):
    """Return True if the interpreted value is the right answer."""
    return value == question["answer"]


def run_quiz(questions, ask=input, tell=print):
    """Run the quiz, never crashing on user input. Return the score."""
    score = 0
    for n, question in enumerate(questions, start=1):
        tell(f"Q{n}. {question['prompt']}")
        if is_correct(question, interpret(question, ask("> "))):
            score += 1
    return score
