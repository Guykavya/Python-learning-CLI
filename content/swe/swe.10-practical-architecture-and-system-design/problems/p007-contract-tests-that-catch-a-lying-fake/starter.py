# Write check functions here: each takes a fresh repository and uses add_member, is_member and members.
# A check raises AssertionError (with a message naming the broken rule) when the repository lies.


def check_adding_twice_is_the_same_as_once(repo):
    repo.add_member(1, "ana")
    repo.add_member(1, "ana")
    assert repo.members(1) == ["ana"], "adding the same member twice must not create a duplicate"


CHECKS = [check_adding_twice_is_the_same_as_once]
