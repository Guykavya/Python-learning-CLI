import uuid

from solution import assign_ids, is_canonical_uuid, new_session_id, user_id

KAVYA = "e20557fa-85ab-5cfa-bef7-ceca88d23d54"
ASHA = "526a2c55-21d3-55ba-8da3-fc2ff6f60c99"


def test_user_id_known_value():
    assert user_id("kavya@example.com") == KAVYA, (
        "user_id is uuid5(uuid.NAMESPACE_URL, 'mailto:' + email) as a str. Check the namespace and the 'mailto:' prefix."
    )
    assert isinstance(user_id("kavya@example.com"), str), "Return str(uuid_object), not the UUID object."


def test_user_id_is_version_5_and_repeatable():
    first = user_id("asha@example.com")
    assert first == user_id("asha@example.com") == ASHA, "uuid5 is computed from the name: the same input must give the same id every time."
    assert uuid.UUID(first).version == 5, "user_id must be a version-5 UUID (uuid5), not a random uuid4."


def test_user_id_normalises():
    assert user_id("  KAVYA@Example.COM \n") == KAVYA, "Strip spaces and lower-case the email before computing the uuid5."
    assert user_id("kavya@example.org") != KAVYA, "A different email must give a different id."


def test_new_session_id_random_v4():
    ids = {new_session_id() for _ in range(200)}
    assert len(ids) == 200, "new_session_id must be random (uuid4): 200 calls should give 200 different ids."
    sample = next(iter(ids))
    assert isinstance(sample, str) and len(sample) == 36, "Return the 36-character string form: str(uuid.uuid4())."
    assert uuid.UUID(sample).version == 4, "Use uuid.uuid4() for random ids (version 4)."


def test_is_canonical_true():
    assert is_canonical_uuid(KAVYA) is True, "The standard hyphenated lowercase form is canonical."
    assert is_canonical_uuid(KAVYA.upper()) is True, "Upper case is accepted too: compare case-insensitively."
    assert is_canonical_uuid(new_session_id()) is True, "A fresh uuid4 string is canonical."


def test_is_canonical_other_accepted_forms_false():
    assert is_canonical_uuid(KAVYA.replace("-", "")) is False, "32 hex digits without hyphens: uuid.UUID accepts it, but it is not the canonical form."
    assert is_canonical_uuid("{" + KAVYA + "}") is False, "Braces are not part of the canonical form."
    assert is_canonical_uuid("urn:uuid:" + KAVYA) is False, "The urn:uuid: prefix is not part of the canonical form."


def test_is_canonical_garbage_false():
    assert is_canonical_uuid("hello") is False, "Not a UUID at all: catch the ValueError from uuid.UUID and return False."
    assert is_canonical_uuid("") is False, "Empty text is not a UUID."
    assert is_canonical_uuid(KAVYA[:-1] + "g") is False, "'g' is not a hex digit."
    assert is_canonical_uuid(KAVYA + " ") is False, "A trailing space makes it non-canonical."


def test_assign_ids():
    result = assign_ids(["Asha@example.com", "asha@example.com", " kavya@example.com"])
    assert result == {"asha@example.com": ASHA, "kavya@example.com": KAVYA}, (
        "Keys are normalised emails (stripped, lower case), so case variants collapse into one entry."
    )
    assert assign_ids([]) == {}, "No emails: empty dict."
