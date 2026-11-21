def check_adding_twice_is_the_same_as_once(repo):
    repo.add_member(1, "ana")
    repo.add_member(1, "ana")
    assert repo.members(1) == ["ana"], "adding the same member twice must not create a duplicate"


def check_membership_ignores_case(repo):
    repo.add_member(1, "Ana")
    assert repo.is_member(1, "ana"), "'Ana' was added, so 'ana' is a member: handles are compared without regard to case"
    assert repo.is_member(1, "ANA"), "'ANA' must be a member too"


def check_handles_are_stored_in_lower_case(repo):
    repo.add_member(1, "Ben")
    repo.add_member(1, "BEN")
    assert repo.members(1) == ["ben"], "members() returns lower-case handles, one per person"


def check_a_stranger_is_not_a_member(repo):
    repo.add_member(1, "ana")
    assert not repo.is_member(1, "cy"), "somebody who was never added must not be a member"
    assert repo.members(2) == [], "a project nobody was added to has no members"


def check_membership_is_per_project(repo):
    repo.add_member(1, "ana")
    assert repo.is_member(1, "ana")
    assert not repo.is_member(2, "ana"), "belonging to project 1 must not make somebody a member of project 2"
    assert repo.members(2) == [], "members(2) must not list project 1's members"


def check_members_are_sorted(repo):
    for handle in ("zoe", "Ana", "ben"):
        repo.add_member(1, handle)
    assert repo.members(1) == ["ana", "ben", "zoe"], "members() is sorted and lower case"


CHECKS = [
    check_adding_twice_is_the_same_as_once,
    check_membership_ignores_case,
    check_handles_are_stored_in_lower_case,
    check_a_stranger_is_not_a_member,
    check_membership_is_per_project,
    check_members_are_sorted,
]
