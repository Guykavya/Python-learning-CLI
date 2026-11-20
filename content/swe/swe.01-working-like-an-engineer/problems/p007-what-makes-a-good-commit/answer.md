## Model answer

History B is better.

**Revert.** `git revert d8e3` removes exactly "use `discount()` in checkout". In history A the same change is spread over several commits together with unrelated edits, so a revert either misses part of the change or throws away good work (the typo fix, the formatting). When each commit has one purpose, undoing a purpose is one command.

**Bisect.** `git bisect` checks out commits in the middle of the history and runs a test. It assumes that every commit can be built and tested. In history A some commits are broken in the middle ("fix tests" exists because the tests failed before), so bisect can blame an innocent commit or stop with "cannot test this one". In B every commit passes, so a failure points at the commit that really introduced it, and a small commit makes the faulty line easy to find.

**Review.** A reviewer reads the diff of each commit: three small, titled commits tell a story (function, use, tests) and can be checked one by one. History A has messages like "wip" and "stuff" and a `.DS_Store` file, so the reviewer must reverse-engineer the intent and gets noise from the formatting change.

**Rules of a good commit**
- one logical change per commit (atomic)
- the project builds and the tests pass at every commit
- a short imperative subject, and a body that says **why** when it is not obvious
- no generated files, caches, secrets or editor files (`.gitignore`)

**Checklist: your answer should mention**
- [ ] **atomic**: one purpose per commit
- [ ] each commit **builds and passes tests**
- [ ] `revert` works on one purpose; mixed commits make it unsafe
- [ ] `bisect` needs working commits in the middle
- [ ] messages that say **what and why** (not "wip"), helpful for review
- [ ] no junk files (`.DS_Store`, caches) in the commits
