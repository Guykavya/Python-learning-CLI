def reserve(db, worker, now, lease=30.0):
    row = db.execute(
        "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_until = ?, worker = ? "
        "WHERE id = (SELECT id FROM jobs WHERE "
        "            (state = 'queued' AND run_at <= ?) OR (state = 'running' AND lease_until <= ?) "
        "            ORDER BY run_at, id LIMIT 1) "
        "RETURNING *",
        (now + lease, worker, now, now),
    ).fetchone()
    return dict(row) if row else None


def complete(db, job_id, worker, now):
    cur = db.execute("UPDATE jobs SET state = 'done', lease_until = NULL "
                     "WHERE id = ? AND worker = ? AND state = 'running'", (job_id, worker))
    return cur.rowcount == 1


def heartbeat(db, job_id, worker, now, lease=30.0):
    cur = db.execute("UPDATE jobs SET lease_until = ? WHERE id = ? AND worker = ? AND state = 'running'",
                     (now + lease, job_id, worker))
    return cur.rowcount == 1
