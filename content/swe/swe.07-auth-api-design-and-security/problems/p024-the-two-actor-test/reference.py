ASHA = {"Authorization": "Bearer t-asha"}
RAVI = {"Authorization": "Bearer t-ravi"}
SECRET = "asha-secret-text"


def check_isolation(make_client) -> list:
    client = make_client()
    problems = []

    # arrange: Asha creates a note
    r = client.post("/notes", json={"text": SECRET}, headers=ASHA)
    if r.status_code != 201:
        return [f"setup: Asha could not create a note (status {r.status_code})"]
    note_id = r.json()["id"]
    path = f"/notes/{note_id}"

    # the owner works (a server that denies everyone would pass every denial check)
    r = client.get(path, headers=ASHA)
    if r.status_code != 200 or r.json().get("text") != SECRET:
        problems.append(f"owner cannot read their own note (status {r.status_code})")

    # read as Ravi and as an anonymous caller
    for who, headers in (("Ravi", RAVI), ("anonymous", {})):
        r = client.get(path, headers=headers)
        if r.status_code not in (401, 404):
            problems.append(f"{who} got status {r.status_code} reading Asha's note (expected 401 or 404)")
        if SECRET in r.text:
            problems.append(f"{who} received Asha's text when reading her note")

    # update as Ravi: refused AND nothing changed
    r = client.patch(path, json={"text": "changed by ravi"}, headers=RAVI)
    if r.status_code != 404:
        problems.append(f"Ravi got status {r.status_code} updating Asha's note (expected 404)")
    after = client.get(path, headers=ASHA)
    if after.status_code != 200 or after.json().get("text") != SECRET:
        problems.append("Asha's note was changed by Ravi's PATCH (side effect, even if the status looked right)")

    # delete as Ravi: refused AND the note survives
    r = client.delete(path, headers=RAVI)
    if r.status_code != 404:
        problems.append(f"Ravi got status {r.status_code} deleting Asha's note (expected 404)")
    if client.get(path, headers=ASHA).status_code != 200:
        problems.append("Asha's note was deleted by Ravi's DELETE")

    # list as Ravi: must not show Asha's note
    r = client.get("/notes", headers=RAVI)
    if r.status_code == 200 and SECRET in r.text:
        problems.append("Ravi's note list contains Asha's note")

    return problems
