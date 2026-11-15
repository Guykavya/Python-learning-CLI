# Turning capstones into a portfolio

A capstone helps you only if someone can see it. Aim for **3 polished projects**, not 12 half-done ones.

## Choose

Pick one capstone from each of three areas that match your target job (`learn capstone` lists them):
a backend service (swe), a data or ML analysis (da / ds / ml), and one of core, dsa or llm.

## Repository checklist

- [ ] Own GitHub repository, one project per repo, a clear name (`churn-prediction-service`, not `project2`)
- [ ] README with the template below
- [ ] `pyproject.toml` or `requirements.txt` that installs from scratch
- [ ] Tests that pass with one command (`pytest`), shown in the README
- [ ] No secrets, no `.venv`, no large data files in git (use a `.gitignore`; link to data instead)
- [ ] Small, meaningful commits; a tag for the finished version
- [ ] A screenshot, a chart or a terminal recording near the top of the README

## README template

```markdown
# Project name
One sentence: what it does and for whom.

## Why
The problem, in two or three lines.

## Demo
Screenshot, chart or a 20-second recording.

## How to run
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pytest
    python -m app

## How it works
A short diagram or list of the parts, and the one design decision you are proudest of.

## Results
Numbers you really measured (accuracy, latency, test count). Say how you measured them.

## What I would do next
Honest limits and next steps.
```

## Résumé bullets

Use the pattern **action + what + measured result**. Only write numbers you measured.

- Built a FastAPI service serving a churn model with request logging and drift checks; 28 tests, p95 latency 40 ms on a laptop.
- Designed a SQL + pandas pipeline that cleans 200k rows and publishes a weekly report; cut manual work from 2 hours to 5 minutes.
- Implemented an LLM tool-use agent with a fake-client test harness, so every behaviour is tested offline.

## Be ready to explain

For each project, prepare answers to:

1. What problem does it solve, and how did you know it worked?
2. What was the hardest bug? How did you find it?
3. What would break first with 100x more data or users?
4. Which decision would you change now, and why?
5. How is it tested? What is not tested?

## Practice

Explain one project aloud in 3 minutes, then in 10. Record yourself once. Ask a friend to try to run it from the README alone.
