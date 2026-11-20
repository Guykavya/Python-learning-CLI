# Each item: (JSON body for POST /tasks, expected status: 201 or 422)
CASES = [
    # valid, including both edges of every range
    ({"title": "Write tests"}, 201),
    ({"title": "x"}, 201),                                      # shortest allowed title
    ({"title": "x" * 100}, 201),                                # longest allowed title
    ({"title": "a", "priority": 1, "tags": ["work"]}, 201),     # lowest priority
    ({"title": "a", "priority": 5}, 201),                       # highest priority
    # invalid: one step past each limit
    ({"title": ""}, 422),                                       # too short
    ({"title": "x" * 101}, 422),                                # too long
    ({"title": "a", "priority": 0}, 422),
    ({"title": "a", "priority": 6}, 422),
    # other rules
    ({"priority": 2}, 422),                                     # title missing
    ({"title": "a", "owner": "asha"}, 422),                     # unknown field
    ({"title": "a", "tags": "work"}, 422),                      # tags must be a list
]
