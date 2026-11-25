# Supervised or unsupervised?

Chapter section 1. In **supervised** learning every training row comes with the answer (a label or a number to predict). In **unsupervised** learning there are no answers: the algorithm looks for structure (groups, unusual points). A careless keyword rule sorts task descriptions:

```python
def family(task):
    t = task.lower()
    if "label" in t or "predict" in t or "forecast" in t or "classify" in t:
        return "supervised"
    if "group" in t or "cluster" in t or "segment" in t or "anomal" in t:
        return "unsupervised"
    return "unclear"


tasks = [
    "Predict house prices from past sales",
    "Group customers by buying habits",
    "Classify emails as spam or not spam",
    "Find unusual card transactions",
    "Forecast next month's sales",
    "Segment shoppers into three clusters",
    "Cluster patients to predict who is at risk",
    "Detect anomalies in server logs",
]
for i, task in enumerate(tasks, start=1):
    print(f"{i}: {family(task)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For the single task `"Label photos of cats"` the program would print `1: supervised`.

## After you answer

- Two of the eight lines are **wrong** as machine-learning statements. Which two, and what is each task really?
