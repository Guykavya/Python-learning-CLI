from solution import price_for, product_info

ASHA = {"name": "asha", "tier": "member"}
RAVI = {"name": "ravi", "tier": "public"}
MEERA = {"name": "meera", "tier": "public"}
SAM = {"name": "sam", "tier": "staff"}


def test_two_users_each_see_their_own_price(db, r):
    assert price_for(r, db, 1, ASHA) == 4490, "Asha is a member: 4490."
    assert price_for(r, db, 1, RAVI) == 4990, \
        "Ravi (public) got Asha's member price from the cache. The key must include everything the price depends on: the tier."


def test_alternating_users(db, r):
    expected = {"member": 4490, "public": 4990, "staff": 2990}
    for _ in range(3):
        for user in (SAM, RAVI, ASHA, MEERA):
            got = price_for(r, db, 1, user)
            assert got == expected[user["tier"]], f"{user['name']} ({user['tier']}) must pay {expected[user['tier']]}, got {got}."


def test_same_tier_shares_the_cache(db, r):
    price_for(r, db, 1, RAVI)
    price_for(r, db, 1, MEERA)
    assert db.price_reads == 1, \
        "Ravi and Meera are both public: the price depends on the tier, not the person, so they must share ONE cache entry. Key by tier, not by user name."


def test_tiers_and_products_are_separate(db, r):
    for user in (ASHA, RAVI, SAM):
        for pid in (1, 2):
            price_for(r, db, pid, user)
    assert db.price_reads == 6, f"3 tiers x 2 products = 6 distinct answers, so 6 database reads; got {db.price_reads}."
    for user in (ASHA, RAVI, SAM):
        for pid in (1, 2):
            price_for(r, db, pid, user)
    assert db.price_reads == 6, "The second round must be served entirely from the cache."


def test_ttl_kept(db, r):
    price_for(r, db, 1, ASHA)
    ttls = [r.ttl(k) for k in r.keys("price:*")]
    assert ttls == [60], f"Keep the price TTL of 60 s on the (single) new key; got TTLs {ttls}."


def test_product_info_still_shared(db, r):
    for user in (ASHA, RAVI, SAM):
        assert product_info(r, db, 2) == {"id": 2, "name": "Monitor"}
    assert db.info_reads == 1, "Product info is the same for everyone: keep ONE shared key, so only one database read."
