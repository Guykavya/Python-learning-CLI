def find_user(users, user_id):
    return users[user_id]


def greeting(users, user_id):
    name = find_user(users, user_id)
    return "Hello, " + name + "!"


def shout_name(users, user_id):
    name = find_user(users, user_id)
    return name.upper()
