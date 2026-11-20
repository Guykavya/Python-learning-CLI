def check_login(make_client):
    # TODO: assert a correct login works and a wrong password gives 401 and no login
    pass


def check_csrf(make_client):
    # TODO: assert that a missing token AND a wrong token are refused with 400, and a right one accepted
    pass


def check_owner_only(make_client):
    # TODO: Asha creates a post; Ravi gets 403 when he deletes it; Asha can delete it (204)
    pass
