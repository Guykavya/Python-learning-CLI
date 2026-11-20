# What makes a good commit?

Two histories contain the **same final code** for a small feature ("discount for orders over 100"):

```text
History A                      History B
---------                      ---------
a1f3 wip                       c7d2 Add discount() to pricing.py
b2e4 stuff                     d8e3 Use discount() in checkout
c3d5 fix                       e9f4 Add tests for discount()
d4e6 more stuff
e5f7 fix tests
f6a8 final, formatted
```

History A mixes the feature, a typo fix, a change to unrelated formatting and a `.DS_Store` file in the same commits; some of its commits do not pass the tests. History B has three commits, each doing one thing, each passing the tests.

In `answer.md` (8 to 12 sentences), explain which history is better and **why**, using three situations:

1. A week later the discount turns out to be wrong in checkout, and you want to take **only that change** out (`git revert`).
2. A bug appeared somewhere in the last 30 commits and you hunt for it with `git bisect` (chapter section 9.7).
3. A teammate reviews the pull request (chapter section 16).

Finish with a short list: what rules does a good commit follow (chapter section 4.1 and 4.2)?
