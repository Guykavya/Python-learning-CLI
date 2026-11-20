## Approach

```python
ASHA = {"Authorization": "Bearer t-asha"}
RAVI = {"Authorization": "Bearer t-ravi"}
SECRET = "asha-secret-text"


def check_isolation(make_client) -> list:
    client = make_client()
    problems = []

    r = client.post("/notes", json={"text": SECRET}, headers=ASHA)       # arrange as Asha
    if r.status_code != 201:
        return [f"setup: Asha could not create a note (status {r.status_code})"]
    path = f"/notes/{r.json()['id']}"

    r = client.get(path, headers=ASHA)                                    # the owner must still work
    if r.status_code != 200 or r.json().get("text") != SECRET:
        problems.append(f"owner cannot read their own note (status {r.status_code})")

    for who, headers in (("Ravi", RAVI), ("anonymous", {})):              # read
        r = client.get(path, headers=headers)
        if r.status_code not in (401, 404):
            problems.append(f"{who} got status {r.status_code} reading Asha's note (expected 401 or 404)")
        if SECRET in r.text:
            problems.append(f"{who} received Asha's text when reading her note")

    r = client.patch(path, json={"text": "changed by ravi"}, headers=RAVI)    # update: status AND side effect
    if r.status_code != 404:
        problems.append(f"Ravi got status {r.status_code} updating Asha's note (expected 404)")
    after = client.get(path, headers=ASHA)
    if after.status_code != 200 or after.json().get("text") != SECRET:
        problems.append("Asha's note was changed by Ravi's PATCH (side effect)")

    r = client.delete(path, headers=RAVI)                                  # delete: status AND survival
    if r.status_code != 404:
        problems.append(f"Ravi got status {r.status_code} deleting Asha's note (expected 404)")
    if client.get(path, headers=ASHA).status_code != 200:
        problems.append("Asha's note was deleted by Ravi's DELETE")

    r = client.get("/notes", headers=RAVI)                                 # list
    if r.status_code == 200 and SECRET in r.text:
        problems.append("Ravi's note list contains Asha's note")
    return problems
```

How each app is caught: the read hole by the read check; the update hole **only** by the second look at Asha's note (the PATCH answered 404, so the status check passes); the list hole by the list check; the deny-everything app by the owner check. The secure app triggers none of them, so the result is `[]`. Note the order: the PATCH check runs before the DELETE check, so a deleted note cannot hide a changed text.

## Complexity

About ten requests per call.

## Another way

Make the checks data: a list of `(who, method, path, json, expected statuses)` rows and a loop, plus a list of "after" checks. The test then reads like the policy table of chapter 7.3 and a new endpoint is one more row. The chapter's meta-test (section 8.4, "Make forgetting impossible") goes one step further and fails when a route has no row.
