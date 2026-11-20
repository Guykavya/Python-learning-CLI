import random

from solution import merge_accounts


def brute(accounts):
    groups = [(acc[0], set(acc[1:])) for acc in accounts]
    changed = True
    while changed:
        changed = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if groups[i][1] & groups[j][1]:
                    merged = (groups[i][0], groups[i][1] | groups[j][1])
                    groups = [g for k, g in enumerate(groups) if k not in (i, j)] + [merged]
                    changed = True
                    break
            if changed:
                break
    result = [[name] + sorted(emails) for name, emails in groups]
    result.sort(key=lambda acc: (acc[0], acc[1]))
    return result


def test_example():
    accounts = [
        ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
        ["John", "johnsmith@mail.com", "john00@mail.com"],
        ["Mary", "mary@mail.com"],
        ["John", "johnnybravo@mail.com"],
    ]
    expected = [
        ["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"],
        ["John", "johnnybravo@mail.com"],
        ["Mary", "mary@mail.com"],
    ]
    got = merge_accounts(accounts)
    assert got == expected, (
        f"Expected {expected}, got {got}. The two Johns that share johnsmith@mail.com are one person (addresses "
        "sorted, no duplicates); the third John shares nothing and stays separate.")


def test_same_name_is_not_same_person():
    got = merge_accounts([["Ann", "a@x"], ["Ann", "b@x"]])
    assert got == [["Ann", "a@x"], ["Ann", "b@x"]], (
        "Two Anns without a shared address are two people. Do not merge by name.")


def test_chain_given_out_of_order():
    accounts = [["Bo", "a@x", "b@x"], ["Bo", "c@x", "d@x"], ["Bo", "b@x", "c@x"]]
    got = merge_accounts(accounts)
    assert got == [["Bo", "a@x", "b@x", "c@x", "d@x"]], (
        "Account 1 and account 2 share nothing directly, but account 3 shares b@x with 1 and c@x with 2: one person. "
        "Merge whole groups (Union-Find), not just two accounts.")


def test_duplicates_inside_one_account():
    got = merge_accounts([["Zed", "z@x", "z@x", "y@x"]])
    assert got == [["Zed", "y@x", "z@x"]], "An address listed twice appears once, and the addresses are sorted."


def test_output_order():
    accounts = [["Bob", "z@x"], ["Al", "q@x"], ["Bob", "c@x"], ["Al", "a@x", "q@x"]]
    got = merge_accounts(accounts)
    assert got == [["Al", "a@x", "q@x"], ["Bob", "c@x"], ["Bob", "z@x"]], (
        "Sort the people by name, then by their first (smallest) address.")


def test_random_against_brute_force():
    rng = random.Random(46)
    for _ in range(200):
        people = rng.randint(1, 6)
        names = [rng.choice(["Ann", "Bo", "Cy"]) for _ in range(people)]
        pool = [[f"p{p}e{k}@x" for k in range(rng.randint(1, 4))] for p in range(people)]
        accounts = []
        for _ in range(rng.randint(1, 10)):
            p = rng.randrange(people)
            emails = [rng.choice(pool[p]) for _ in range(rng.randint(1, 3))]
            accounts.append([names[p]] + emails)
        rng.shuffle(accounts)
        assert merge_accounts(accounts) == brute(accounts), f"accounts={accounts}: expected {brute(accounts)}."


def test_bigger_input():
    n = 1000
    accounts = [["Kim", f"e{i}@x", f"e{i + 1}@x"] for i in range(0, 2 * n, 2)]
    accounts += [["Kim", f"e{i + 1}@x", f"e{i + 2}@x"] for i in range(0, 2 * n - 2, 2)]
    got = merge_accounts(accounts)
    assert len(got) == 1 and len(got[0]) == 1 + 2 * n, (
        "2,000 accounts linked in one long chain: one person with all 2,000 addresses.")
