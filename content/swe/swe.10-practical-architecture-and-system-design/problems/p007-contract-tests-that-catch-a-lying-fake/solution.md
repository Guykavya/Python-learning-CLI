## Approach

Think like a person who wants to break the fake: for each way a fake can differ from the real repository, one scenario in which the two answer differently.

```python
def check_membership_ignores_case(repo):
    repo.add_member(1, "Ana")
    assert repo.is_member(1, "ana"), "'Ana' was added, so 'ana' is a member: handles are compared without regard to case"

def check_membership_is_per_project(repo):
    repo.add_member(1, "ana")
    assert not repo.is_member(2, "ana"), "belonging to project 1 must not make somebody a member of project 2"
```

The test then runs every check on the honest repositories (they must all pass, otherwise the check describes a rule that is **not** in the interface) and on each liar (at least one check must fail). Passing on the honest ones and failing on the liars is what makes a contract suite trustworthy; the same mindset is used in **mutation testing**: change the code in a small wrong way and make sure some test notices.

## Cost

A handful of five-line functions. They run in microseconds on a fake and are reused unchanged when a second real implementation (PostgreSQL) appears: that is when the contract suite pays.

## Another way

With `pytest` you would write the checks as test functions parametrized over `["fake", "sqlite"]` (as in p006) and keep them in one file next to the repository. Here they are plain functions in a list so that the exercise can run them against implementations you cannot see.
