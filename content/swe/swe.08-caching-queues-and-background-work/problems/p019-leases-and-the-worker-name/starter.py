def reserve(db, worker, now, lease=30.0):
    # TODO: claim the next ready job in ONE statement and return it as a dict
    return None


def complete(db, job_id, worker, now):
    # TODO: only the current lease holder may complete
    return False


def heartbeat(db, job_id, worker, now, lease=30.0):
    # TODO: extend the lease, only for the current holder
    return False
