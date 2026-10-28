import uuid


def _normalise(email):
    return email.strip().lower()


def user_id(email):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "mailto:" + _normalise(email)))


def new_session_id():
    return str(uuid.uuid4())


def is_canonical_uuid(text):
    try:
        parsed = uuid.UUID(text)
    except (ValueError, TypeError, AttributeError):
        return False
    return str(parsed) == text.lower()


def assign_ids(emails):
    return {_normalise(email): user_id(email) for email in emails}
