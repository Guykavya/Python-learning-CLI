def token(client):
    return client.get("/csrf").get_data(as_text=True)


def log_in(client, username, password):
    return client.post("/login", data={"username": username, "password": password, "csrf_token": token(client)})


def create_post(client, title="hello", csrf=None):
    data = {"title": title}
    if csrf is not False:
        data["csrf_token"] = token(client) if csrf is None else csrf   # login cleared the session: ask for the token again
    return client.post("/posts", data=data)


def check_login(make_client):
    client = make_client()
    r = log_in(client, "asha", "pw-asha")
    assert r.status_code == 200, f"a correct login must work, got {r.status_code}"
    assert create_post(client).status_code == 201, "after logging in, the session must allow creating a post"

    wrong = make_client()
    r = log_in(wrong, "asha", "not-the-password")
    assert r.status_code == 401, f"a wrong password must give 401, got {r.status_code}"
    assert create_post(wrong).status_code == 401, "a failed login must not leave the user logged in"


def check_csrf(make_client):
    client = make_client()
    assert log_in(client, "asha", "pw-asha").status_code == 200
    assert create_post(client, csrf=False).status_code == 400, "a POST without a CSRF token must be refused (400)"
    assert create_post(client, csrf="wrong-token").status_code == 400, "a POST with a WRONG CSRF token must be refused (400)"
    assert create_post(client).status_code == 201, "a POST with the right token must work"


def check_owner_only(make_client):
    asha, ravi = make_client(), make_client()
    assert log_in(asha, "asha", "pw-asha").status_code == 200
    assert log_in(ravi, "ravi", "pw-ravi").status_code == 200
    post_id = create_post(asha).get_json()["id"]

    r = ravi.post(f"/posts/{post_id}/delete", data={"csrf_token": token(ravi)})
    assert r.status_code == 403, f"Ravi must not delete Asha's post (403), got {r.status_code}"
    r = asha.post(f"/posts/{post_id}/delete", data={"csrf_token": token(asha)})
    assert r.status_code == 204, f"the author must still be able to delete the post (204), got {r.status_code}"
