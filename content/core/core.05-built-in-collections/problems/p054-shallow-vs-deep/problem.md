# Shallow copy versus deep copy

Look at this program:

```python
import copy
team = [["Asha", 82], ["Ravi", 75]]
alias = team
shallow = team.copy()
deep = copy.deepcopy(team)
team[0][1] = 90
team.append(["Meena", 88])
print(alias)
print(shallow)
print(deep)
```

It prints:

```
[['Asha', 90], ['Ravi', 75], ['Meena', 88]]
[['Asha', 90], ['Ravi', 75]]
[['Asha', 82], ['Ravi', 75]]
```

Explain in your own words, in `answer.md`:

1. What `alias = team` creates, and why `alias` shows both changes.
2. What `team.copy()` creates. Why does `shallow` show the new mark 90 but not Meena?
3. What `copy.deepcopy` creates, and why `deep` shows neither change.
4. Draw a memory diagram (text is fine) showing the outer lists and the inner lists after the
   copies are made.
5. Two other ways to make a shallow copy of a list, and one way to deep-copy a list of lists of
   numbers or strings without the `copy` module.
